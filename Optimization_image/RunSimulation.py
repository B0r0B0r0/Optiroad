import json
import torch
import traci
import os
# Common device setup for GPU
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def simulation_observations(sumocfg_path: str):
    traci.start(["sumo", "-c", f"{sumocfg_path}.sumocfg"])
    wait_per_edge = {}
    total_waiting_time = 0.0
    vehicles_per_edge = {}
    pressure_per_tls = {}
    mains = {}
    sec = {}

    traci.close()


def run_simulation_and_measure_waiting_time(sumocfg_path):
    traci.start(["sumo", "-c", f"{sumocfg_path}.sumocfg"])
    

    total_waiting_time = 0.0
    vehicle_waiting = {}
    sim_step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        sim_step += 1
        for veh_id in traci.vehicle.getIDList():
            wait = traci.vehicle.getWaitingTime(veh_id)
            prev = vehicle_waiting.get(veh_id, 0.0)
            if wait == 0.0 and prev > 0.0:
                total_waiting_time += prev
            vehicle_waiting[veh_id] = wait

    traci.close()
    return total_waiting_time, len(vehicle_waiting)



def run_simulation_and_measure_waiting_time_per_tls(
    network_path: str,
    max_steps: int = 100000
):
    """
    Run SUMO and measure cumulative waiting time per traffic light using GPU for delta computations.
    Returns (total_wait, arrived_vehicle_count, waits_per_tls).
    """
    # Load TLS logic
    with open(f"{network_path}.ttl.json") as f:
        ttl_logic = json.load(f)
    tls_ids = list(ttl_logic.keys())

    # Precompute inbound lanes per TLS and flatten
    traci.start([
        "sumo", "-c", f"{network_path}.sumocfg",
        "--waiting-time-memory", "10000",
        "--time-to-teleport", "-1"
    ])
    inbound_lanes = {}
    for tls in tls_ids:
        links = traci.trafficlight.getControlledLinks(tls)
        lanes = sorted({link[0] for group in links for link in group})
        inbound_lanes[tls] = lanes
    traci.close()

    # Flatten all lanes and record slices per TLS
    all_lanes = []
    lane_slices = {}
    idx = 0
    for tls in tls_ids:
        lanes = inbound_lanes[tls]
        length = len(lanes)
        lane_slices[tls] = (idx, idx + length)
        all_lanes.extend(lanes)
        idx += length

    # Initialize prev_wait tensor and accumulators
    prev_wait = torch.zeros(idx, device=DEVICE)
    waits_per_tls = {tls: 0.0 for tls in tls_ids}

    # Run simulation
    traci.start([
        "sumo", "-c", f"{network_path}.sumocfg",
        "--waiting-time-memory", "10000",
        "--time-to-teleport", "-1",
        "--mesosim", "true"
    ])
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
        traci.simulationStep()
        step += 1

        # gather all waiting times in one tensor
        curr_wait = torch.tensor(
            [traci.lane.getWaitingTime(l) for l in all_lanes],
            device=DEVICE
        )
        # compute positive deltas in parallel
        delta = curr_wait - prev_wait
        positive = torch.clamp(delta, min=0.0)

        # aggregate per TLS
        for tls, (start, end) in lane_slices.items():
            waits_per_tls[tls] += positive[start:end].sum().item()

        prev_wait = curr_wait

    total_wait = sum(waits_per_tls.values())
    arrived = traci.simulation.getArrivedNumber()
    traci.close()
    return total_wait, arrived, waits_per_tls



def run_simulation_and_measure_waiting_time_per_edge(
    network_path: str,
    max_steps: int = 100000
):
    """
    Run SUMO and measure cumulative waiting time per incoming edge at each TLS using GPU.
    Returns (total_wait, arrived_vehicle_count, waits_per_edge_per_tls).
    """
    # Load TLS logic
    with open(f"{network_path}.ttl.json") as f:
        ttl_logic = json.load(f)
    tls_ids = list(ttl_logic.keys())

    # Precompute lanes and edges for each TLS then flatten
    traci.start([
        "sumo", "-c", f"{network_path}.sumocfg",
        "--waiting-time-memory", "10000",
        "--time-to-teleport", "-1"
    ])
    edge_lanes = {}
    for tls in tls_ids:
        links = traci.trafficlight.getControlledLinks(tls)
        lanes = sorted({link[0] for group in links for link in group})
        edges = sorted({l.split('_')[0] for l in lanes})
        edge_lanes[tls] = {edge: [l for l in lanes if l.startswith(edge + "_")] for edge in edges}
    traci.close()

    # Flatten all lanes across all (tls,edge) and record slices
    all_lanes = []
    slice_map = {}  # (tls,edge) -> (start,end)
    idx = 0
    for tls in tls_ids:
        for edge, lanes in edge_lanes[tls].items():
            length = len(lanes)
            slice_map[(tls, edge)] = (idx, idx + length)
            all_lanes.extend(lanes)
            idx += length

    # Initialize prev_wait and accumulators
    prev_wait = torch.zeros(idx, device=DEVICE)
    waits_per_edge = {tls: {edge: 0.0 for edge in edge_lanes[tls]} for tls in tls_ids}

    # Run simulation
    traci.start([
        "sumo", "-c", f"{network_path}.sumocfg",
        "--waiting-time-memory", "10000",
        "--time-to-teleport", "-1",
        "--mesosim", "true"
    ])
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
        traci.simulationStep()
        step += 1

        curr_wait = torch.tensor(
            [traci.lane.getWaitingTime(l) for l in all_lanes],
            device=DEVICE
        )
        delta = curr_wait - prev_wait
        positive = torch.clamp(delta, min=0.0)

        # aggregate per edge per TLS
        for (tls, edge), (start, end) in slice_map.items():
            waits_per_edge[tls][edge] += positive[start:end].sum().item()

        prev_wait = curr_wait

    total_wait = sum(
        sum(edges.values()) for edges in waits_per_edge.values()
    )
    arrived = traci.simulation.getArrivedNumber()
    traci.close()
    return total_wait, arrived, waits_per_edge


def run_simulation_and_measure_mean(sumocfg_path):
    traci.start(["sumo", "-c", f"{sumocfg_path}.sumocfg"])
    

    total_waiting_time = 0.0
    vehicle_waiting = {}
    mean_vector = []
    sim_step = 0

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        sim_step += 1
        for veh_id in traci.vehicle.getIDList():
            wait = traci.vehicle.getWaitingTime(veh_id)
            prev = vehicle_waiting.get(veh_id, 0.0)
            if wait == 0.0 and prev > 0.0:
                total_waiting_time += prev
            vehicle_waiting[veh_id] = wait

        if sim_step % 600 == 0:
            mean_vector.append(total_waiting_time/len(vehicle_waiting))


    traci.close()
    return total_waiting_time, mean_vector

