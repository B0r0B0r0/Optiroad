from collections import defaultdict
import os
import shutil
import json
import numpy as np
import gym
from gym import spaces
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Normal
from RunSimulation import run_simulation_and_measure_waiting_time
from TrafficLightLogic import extract_phases_from_json, get_main_and_sec, get_sim_cars, update_phases_from_json, get_nr_tls, get_traffic_lights
import traci
from pymongo import MongoClient
import io, bson
from datetime import datetime
from config import MONGO_URI

class SumoTrafficEnv(gym.Env):
    """
    Gym environment for SUMO traffic light optimization via PPO.

    Observations:
      - For each traffic light: [avg_vehicles_waiting, avg_wait_time]
    Actions:
      - Offset adjustments per phase (non-yellow), within [-offset_limit, offset_limit].
    Episode:
      - One full simulation run, single step.
    """
    def __init__(self, sumopath, min_duration=3.0, max_duration=90.0):
        super().__init__()
        self.sumopath = sumopath
        self.net_file = sumopath + ".net.xml"

        ttl_json = self.sumopath + ".ttl.json"
        if not os.path.exists(ttl_json):
            raise FileNotFoundError(f"Missing phase JSON: {ttl_json}")
        self.num_cars = get_sim_cars(self.sumopath)
        # extrage toate fazele și construiește o mască pentru cele care NU sunt galbene
        all_phases = extract_phases_from_json(self.sumopath)
        self.mask_non_yellow = []
        with open(ttl_json, 'r') as f:
            base = json.load(f)
            idx = 0
            for tl_id, data in base.items():
                for phase in data['phases']:
                    if 'y' not in phase['state']:
                        self.mask_non_yellow.append(idx)
                    idx += 1

        self.initial_phases = np.array([all_phases[i] for i in self.mask_non_yellow], dtype=np.float32)
        self.current_phases = self.initial_phases.copy()
        self.n_phases = len(self.initial_phases)
        self.n_tls = get_nr_tls(self.sumopath)
        self.tl_ids = get_traffic_lights(self.sumopath)
        self.tl_ids = get_main_and_sec(self.sumopath, self.tl_ids)
        self.min_duration = float(min_duration)
        self.max_duration = float(max_duration)
        self.offset_limit = 45.0  

        self.action_space = spaces.Box(
            low=np.full(self.n_phases, -self.offset_limit, dtype=np.float32),
            high=np.full(self.n_phases, self.offset_limit, dtype=np.float32),
            shape=(self.n_phases,),
            dtype=np.float32
        )

        self.observation_space = spaces.Box(
            low=0.0, high=np.inf, shape=(self.n_tls, 5), dtype=np.float32
        )  # avg_vehicles_waiting, avg_wait_time, total_waiting_time, total_generated_vehicles, pressure

        # aplicăm fazele inițiale și calculăm baseline
        full_phases = extract_phases_from_json(self.sumopath)
        for i, idx in enumerate(self.mask_non_yellow):
            full_phases[idx] = self.current_phases[i]
        self._apply_phases(np.array(full_phases, dtype=np.float32))

        returns = self.simulate(self.sumopath)
        self.base_waiting = returns[list(self.tl_ids.keys())[0]]["total_waiting_time"]

    def _apply_phases(self, durations: np.ndarray):
        with open(self.sumopath + ".ttl.json", 'r') as f:
            base = json.load(f)
        updates = {}
        idx = 0
        for tl_id, data in base.items():
            phases = []
            for phase in data['phases']:
                state_str = phase['state']
                if 'y' in state_str:
                    d = phase['duration']  # nu modificăm fazele galbene
                else:
                    d = int(np.clip(durations[idx], self.min_duration, self.max_duration))
                idx += 1
                phases.append({'duration': d, 'state': state_str})
            updates[tl_id] = {'phases': phases}
        with open(self.sumopath + ".ttl.update.json", 'w') as f:
            json.dump(updates, f, indent=2)
        update_phases_from_json(self.sumopath, self.sumopath)

    def reset(self):
        full_phases = extract_phases_from_json(self.sumopath)
        for i, idx in enumerate(self.mask_non_yellow):
            full_phases[idx] = self.current_phases[i]
        self._apply_phases(np.array(full_phases, dtype=np.float32))

        obs_aux = self.simulate(self.sumopath)

        obs = np.array([
            [
            obs_aux[tls_id]["avg_veh_wait"],
            obs_aux[tls_id]["avg_wait_per_tls"],
            obs_aux[tls_id]["total_waiting_time"],
            obs_aux[tls_id]["avg_veh_per_tls"],
            obs_aux[tls_id]["pressure"]
            ]
            for tls_id in self.tl_ids
        ], dtype=np.float32)

        info = {
            'base_waiting': self.base_waiting,
            'new_waiting': self.base_waiting,  # initial waiting time is the baseline),
            'accepted': "accepted"
        }
        reward = self.base_waiting - info['new_waiting']
        return obs, float(reward), True, info
    
    
    def simulate(self, sumopath):        
        edge_waits = {
            tls_id: {
                'main': {
                    edge: {'wait_edge': 0.0, 'veh_edge': 0}
                    for edge in cluster['main']
                },
                'sec': {
                    edge: {'wait_edge': 0.0, 'veh_edge': 0}
                    for edge in cluster['sec']
                }
            }
            for tls_id, cluster in self.tl_ids.items()
        }

        edge_auxiliary = {
            tls_id: {
                'main': {
                    edge: {'wait_edge': 0.0, 'veh_edge': 0}
                    for edge in cluster['main']
                },
                'sec': {
                    edge: {'wait_edge': 0.0, 'veh_edge': 0}
                    for edge in cluster['sec']
                }
            }
            for tls_id, cluster in self.tl_ids.items()
        }

        total_wait = 0
        traci.start(["sumo", "-c", f"{sumopath}.sumocfg"])
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            for tls_id in self.tl_ids:
                for group in ['main', 'sec']:
                    for edge_id in self.tl_ids[tls_id][group]:
                        wait_time = traci.edge.getWaitingTime(edge_id)
                        veh = traci.edge.getLastStepVehicleNumber(edge_id)
                        if wait_time > edge_auxiliary[tls_id][group][edge_id]['wait_edge']:
                            edge_auxiliary[tls_id][group][edge_id]['wait_edge'] = wait_time
                            edge_auxiliary[tls_id][group][edge_id]['veh_edge'] = veh
                        else:
                            edge_waits[tls_id][group][edge_id]['wait_edge'] += edge_auxiliary[tls_id][group][edge_id]['wait_edge']
                            edge_waits[tls_id][group][edge_id]['veh_edge'] += edge_auxiliary[tls_id][group][edge_id]['veh_edge']
                            edge_auxiliary[tls_id][group][edge_id]['wait_edge'] = 0.0
                            edge_auxiliary[tls_id][group][edge_id]['veh_edge'] = 0.0

        traci.close()
        tls_waits = {}
        tls_vehs = {}
        pressures = {}
        for tls_id in self.tl_ids:
            tls_wait=0.0
            tls_veh=0
            for group in ['main', 'sec']:
                for edge_id, data in edge_waits[tls_id][group].items():
                    total_wait += data['wait_edge']
                    tls_wait += data['wait_edge']
                    tls_veh += data['veh_edge']
            if tls_veh != 0:
                tls_waits[tls_id] = tls_wait / tls_veh
            else:
                tls_waits[tls_id] = 0.0
            tls_vehs[tls_id] = tls_veh / self.num_cars
            main_veh = sum(edge_waits[tls_id]['main'][e]['veh_edge'] for e in edge_waits[tls_id]['main'])
            sec_veh = sum(edge_waits[tls_id]['sec'][e]['veh_edge'] for e in edge_waits[tls_id]['sec'])
            pressures[tls_id] = (main_veh - sec_veh) 
        avg_veh_wait = total_wait / self.num_cars
        returns = {}
        for tls_id in self.tl_ids:
            returns[tls_id] = {
                "avg_veh_wait": avg_veh_wait,
                "avg_wait_per_tls": tls_waits[tls_id],
                "total_waiting_time": total_wait/self.num_cars,
                "avg_veh_per_tls": tls_vehs[tls_id],
                "pressure": pressures[tls_id]
            }

        # avg_vehicles_waiting, avg_wait_time_per_tls, total_waiting_time, avg_veh_per_tls, pressure
        return returns

    def step(self, action: np.ndarray):
        action = np.clip(action, -self.offset_limit, self.offset_limit)
        
        full_phases = extract_phases_from_json(self.sumopath)
        for i, idx in enumerate(self.mask_non_yellow):
            full_phases[idx] += action[i]
        full_phases = np.array(full_phases, dtype=np.float32)

        self._apply_phases(full_phases)

        obs_aux = self.simulate(self.sumopath)


        obs = np.array([
            [
            obs_aux[tls_id]["avg_veh_wait"],
            obs_aux[tls_id]["avg_wait_per_tls"],
            obs_aux[tls_id]["total_waiting_time"],
            obs_aux[tls_id]["avg_veh_per_tls"],
            obs_aux[tls_id]["pressure"]
            ]
            for tls_id in self.tl_ids
        ], dtype=np.float32)
        
        info = {
            'base_waiting': self.base_waiting,
            'new_waiting': list(obs_aux.values())[0]["total_waiting_time"],
            'accepted': bool(self.base_waiting - list(obs_aux.values())[0]["total_waiting_time"] < 0.0)
        }


        reward = self.base_waiting - info['new_waiting']
        return obs, float(reward), True, info

class RolloutBuffer:
    def __init__(self):
        self.states = []
        self.actions = []
        self.logprobs = []
        self.rewards = []
        self.is_terminals = []
    def clear(self):
        self.states.clear(); self.actions.clear(); self.logprobs.clear()
        self.rewards.clear(); self.is_terminals.clear()

class ActorCritic(nn.Module):
    def __init__(self, state_dim: int, action_dim: int, offset: float = 45.0):
        super().__init__()
        self.offset = offset

        # actor network
        self.actor = nn.Sequential(
            nn.Linear(state_dim, 64), nn.Tanh(),
            nn.Linear(64, 64), nn.Tanh(),
            nn.Linear(64, action_dim),
            nn.Tanh()  # output în [-1, 1]
        )

        # critic network
        self.critic = nn.Sequential(
            nn.Linear(state_dim, 64), nn.Tanh(),
            nn.Linear(64, 64), nn.Tanh(),
            nn.Linear(64, 1)
        )

        # log std pentru distribuția Gaussiană
        self.log_std = nn.Parameter(torch.zeros(action_dim))

        # scalare acțiuni: de la [-1, 1] la [min_duration, max_duration]
        self.register_buffer("action_scale", torch.tensor(-5.0))
        self.register_buffer("action_bias", torch.tensor(5.0))

    def scale_action(self, raw_action):
        # scalează de la [-1, 1] la [min, max]
        return raw_action * self.action_scale + self.action_bias

    def act(self, state: torch.Tensor, buffer: RolloutBuffer):
        mean = self.actor(state)  # ∈ [-1, 1]
        std = torch.exp(self.log_std)
        dist = Normal(mean, std)
        action = dist.sample()
        logprob = dist.log_prob(action).sum(dim=-1)
        buffer.states.append(state)
        buffer.actions.append(action)
        buffer.logprobs.append(logprob)
        return action.detach(), logprob.detach()

    def evaluate(self, states: torch.Tensor, actions: torch.Tensor):
        means = self.actor(states)
        means = self.scale_action(means)
        std = torch.exp(self.log_std)
        dist = Normal(means, std)
        logprobs = dist.log_prob(actions).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        values = self.critic(states).squeeze(-1)
        return logprobs, values, entropy

class PPO:
    def __init__(self, state_dim: int, action_dim: int,
                 lr=3e-4, gamma=0.99, k_epochs=10,
                 eps_clip=0.2, ent_coef=0.01,
                 vf_coef=0.5, max_grad_norm=0.5):
        self.buffer = RolloutBuffer()
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.k_epochs = k_epochs
        self.ent_coef = ent_coef
        self.vf_coef = vf_coef
        self.max_grad_norm = max_grad_norm
        # initialize policy and old policy
        self.policy = ActorCritic(state_dim, action_dim)
        self.policy_old = ActorCritic(state_dim, action_dim)
        self.policy_old.load_state_dict(self.policy.state_dict())
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        self.MseLoss = nn.MSELoss()

    def select_action(self, state: np.ndarray):
        tensor = torch.FloatTensor(state)
        with torch.no_grad():
            action, logprob = self.policy_old.act(tensor, self.buffer)
        return action.numpy(), logprob.numpy()

    def store_reward(self, reward: float, done: bool):
        self.buffer.rewards.append(reward)
        self.buffer.is_terminals.append(done)

    def update(self):
        # compute discounted returns
        returns = []
        discounted = 0
        for r, done in zip(reversed(self.buffer.rewards), reversed(self.buffer.is_terminals)):
            if done:
                discounted = 0
            discounted = r + self.gamma * discounted
            returns.insert(0, discounted)
        # convert to tensor
        rewards = torch.tensor(returns, dtype=torch.float32)
        # normalize if possible
        if rewards.numel() > 1:
            rewards = (rewards - rewards.mean()) / (rewards.std(unbiased=False) + 1e-7)
        else:
            rewards = rewards - rewards.mean()
        # stack states and actions
        states = torch.stack(self.buffer.states)
        actions = torch.stack(self.buffer.actions)
        old_logprobs = torch.stack(self.buffer.logprobs)
        # PPO updates
        for _ in range(self.k_epochs):
            logprobs, state_vals, entropy = self.policy.evaluate(states, actions)
            ratios = torch.exp(logprobs - old_logprobs)
            adv = rewards - state_vals.detach()
            surr1 = ratios * adv
            surr2 = torch.clamp(ratios, 1-self.eps_clip, 1+self.eps_clip) * adv
            loss = -torch.min(surr1, surr2).mean() \
                   + self.vf_coef * self.MseLoss(state_vals, rewards) \
                   - self.ent_coef * entropy.mean()
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)
            self.optimizer.step()
        # sync old policy
        self.policy_old.load_state_dict(self.policy.state_dict())
        self.buffer.clear()

   
    def save_model_to_mongo(self, mongo_uri, location: dict, window: dict, rewards: list):
        """
        Salvează modelul PPO și recompensele în MongoDB.

        location = {"country": ..., "county": ..., "city": ...}
        window = {"day": "Monday", "start": "08:00", "end": "09:00"}
        """

        try:
            client = MongoClient(mongo_uri)
            db = client["ppo_results"]
            collection = db["ppo_models"]

            # serializare model în buffer binar
            buffer = io.BytesIO()
            torch.save(self.policy.state_dict(), buffer)
            weights_binary = bson.Binary(buffer.getvalue())

            doc = {
                "location": location,
                "window": {
                    "day": window["day"],
                    "start": window["start"],
                    "end": window["end"]
                },
                "timestamp": datetime.utcnow(),
                "model_weights": weights_binary,
                "rewards": rewards
            }

            # update cu upsert
            collection.update_one(
                {
                    "location": location,
                    "window.day": window["day"],
                    "window.start": window["start"],
                    "window.end": window["end"]
                },
                {"$set": doc},
                upsert=True
            )

            print("[MongoDB] ✅ Model salvat cu succes.")
        except Exception as e:
            print(f"[MongoDB] ❌ Eroare la salvare: {e}")

    def load_model_from_mongo(self, mongo_uri, location: dict, window: dict):
        """
        Încarcă modelul PPO din MongoDB dacă există.

        location = {"country": ..., "county": ..., "city": ...}
        window = {"day": "Monday", "start": "08:00", "end": "09:00"}
        """
        from pymongo import MongoClient
        import io

        try:
            client = MongoClient(mongo_uri)
            db = client["ppo_results"]
            collection = db["ppo_models"]

            # caută documentul în funcție de cheie compusă
            doc = collection.find_one({
                "location": location,
                "window.day": window["day"],
                "window.start": window["start"],
                "window.end": window["end"]
            })

            if doc and "model_weights" in doc:
                buffer = io.BytesIO(doc["model_weights"])
                state_dict = torch.load(buffer)
                self.policy.load_state_dict(state_dict)
                self.policy_old.load_state_dict(state_dict)
                print("[MongoDB] ✅ Model încărcat cu succes.")
                return True
            else:
                print("[MongoDB] ⚠️ Modelul nu există în baza de date.")
                return False

        except Exception as e:
            print(f"[MongoDB] ❌ Eroare la încărcare: {e}")
            return False



def trainPPO(sumopath, country, county, city, start_time, end_time, day, max_episodes=50):
    env = SumoTrafficEnv(sumopath)
    agent = PPO(   # inițializezi agentul
        state_dim=env.observation_space.shape[0] * env.observation_space.shape[1],
        action_dim=env.action_space.shape[0]
    )

    if agent.load_model_from_mongo(
        mongo_uri=MONGO_URI,
        location={"country": country, "county": county, "city": city},
        window={
            "day": day,
            "start": start_time,
            "end": end_time
    },):
        print("Model loaded from MongoDB - continuing training...")
    else:
        print("No existing model found - training from scratch.")

    # 1) Reset și baseline o singură dată
    obs, reward, _, _ = env.reset()   # aplică initial phases + măsoară base_waiting
    state = obs.flatten()  # dacă ai flatten
    actions = {}
    rewards = []
    best_reward = reward 
    best_action = None
    # 2) Loop de episoade fără reset
    for ep in range(1, max_episodes+1):
        # agentul alege offset-ul pe baza ultimelor observații
        action, _ = agent.select_action(state)
        actions[ep] = action
        # aplică și simulează un pas întreg
        obs, reward, done, info = env.step(action)
        state = obs.flatten()  # actualizăm starea pentru pasul următor
        
        rewards.append(reward)
        # stocăm recompensa și antrenăm

        agent.store_reward(reward, done)
        agent.update()

        print(f"Ep {ep} | Base {info['base_waiting']:.2f} | New {info['new_waiting']:.2f} | Reward {reward:.2f}")

        if reward > best_reward:
            best_reward = reward
            best_action = action.copy()
            full_phases = extract_phases_from_json(env.sumopath)
            for i, idx in enumerate(env.mask_non_yellow):
                full_phases[idx] += action[i]
            full_phases = np.array(full_phases, dtype=np.float32)

            env._apply_phases(full_phases)



        
    agent.save_model_to_mongo(
    mongo_uri=MONGO_URI,
    location={"country": country, "county": county, "city": city},
    window={
        "day": day,
        "start": start_time,
        "end": end_time
    },
    rewards=rewards
)



    return

