from sumolib.net import readNet
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import json
import os
from collections import defaultdict
import traci
import time


#### POSSIBLE DEPRECATION ####
def add_additional_file_to_sumocfg(file_path):
    sumocfg_path = file_path + ".sumocfg"
    additional_file = file_path.split("/")[-1] + ".tll.xml"

    tree = ET.parse(sumocfg_path)
    root = tree.getroot()

    input_tag = root.find("input")
    if input_tag is None:
        input_tag = ET.SubElement(root, "input")

    add_tag = input_tag.find("additional-files")

    if add_tag is None:
        add_tag = ET.SubElement(input_tag, "additional-files")
        add_tag.set("value", additional_file)
    else:
        current_value = add_tag.get("value")
        files = [f.strip() for f in current_value.split(",")]

        if additional_file not in files:
            files.append(additional_file)
            add_tag.set("value", ", ".join(files))

    tree.write(sumocfg_path)

def ttl_init(net_file, output_json="traffic_logic.json"):
    net = readNet(net_file + ".net.xml")
    logic = {}

    tls_list = net.getTrafficLights()

    for tls in tls_list:
        tls_id = tls.getID()

        phases = [
            {"duration": 30, "state": "Gr"},
            {"duration": 5,  "state": "yr"},
            {"duration": 30, "state": "rG"},
            {"duration": 5,  "state": "ry"}
        ]

        logic[tls_id] = {"phases": phases}

    with open(output_json, "w") as f:
        json.dump(logic, f, indent=2)


def update_ttl_init(tll_file, update_json_file):
    tree = ET.parse(tll_file+".tll.xml")
    root = tree.getroot()

    with open(update_json_file, "r") as f:
        updates = json.load(f)

    updated = []
    not_found = []

    for tl_id, new_logic in updates.items():
        found = False
        for tlLogic in root.findall("tlLogic"):
            if tlLogic.get("id") == tl_id:
                found = True
                for phase in list(tlLogic.findall("phase")):
                    tlLogic.remove(phase)

                for phase_data in new_logic["phases"]:
                    ET.SubElement(
                        tlLogic,
                        "phase",
                        duration=str(phase_data["duration"]),
                        state=phase_data["state"]
                    )

                updated.append(tl_id)
                break

        if not found:
            not_found.append(tl_id)

    tree.write(tll_file+".tll.xml")
    if not_found:
        pass
#### END OF POSSIBLE DEPRECATION ####

#### In use ####

def get_traffic_lights(net_file):
    net = readNet(net_file + ".net.xml")
    traffic_lights = []

    for node in net.getNodes():
        if node.getType() == "traffic_light":
            traffic_lights.append(node.getID())
            #print(f"Am găsit un semafor la intersecția: {node.getID()}")

    return traffic_lights


def get_nr_tls(net_file):
    net = readNet(net_file + ".net.xml")
    count = 0

    for node in net.getNodes():
        if node.getType() == "traffic_light":
            count += 1

    return count

def extract_phases_to_json(xml_path, output_json="traffic_logic"):
    tree = ET.parse(xml_path+".net.xml")
    root = tree.getroot()

    logic = {}

    for tlLogic in root.findall("tlLogic"):
        tls_id = tlLogic.get("id")
        phases = []

        for phase in tlLogic.findall("phase"):
            phases.append({
                "duration": int(phase.get("duration")),
                "state": phase.get("state")
            })

        logic[tls_id] = {"phases": phases}

    with open(output_json+".ttl.json", "w") as f:
        json.dump(logic, f, indent=2)

def extract_phases_to_json2(xml_path, output_json="traffic_logic"):
    tree = ET.parse(xml_path + ".net.xml")
    root = tree.getroot()

    logic = {}
    intersections = defaultdict(list)

    # 🧠 Construim mapare tls_id → node_id pe baza junction-urilor
    tls_to_node = {}

    for junction in root.findall("junction"):
        if junction.get("type") == "traffic_light":
            node_id = junction.get("id")
            tls_id = node_id  # în SUMO, tls_id = node_id pentru semafoare simple
            tls_to_node[tls_id] = node_id  # redundanță, dar utilă pt consistență

    # 🧱 Construim TTL logic + grupare pe intersecții
    for tlLogic in root.findall("tlLogic"):
        tls_id = tlLogic.get("id")
        node_id = tls_to_node.get(tls_id, "unknown")

        phases = []
        for phase in tlLogic.findall("phase"):
            phases.append({
                "duration": int(phase.get("duration")),
                "state": phase.get("state")
            })

        logic[tls_id] = {
            "phases": phases
        }

        intersections[node_id].append(tls_id)

    # 💾 Scriem logic TTL
    with open(output_json + ".ttl.json", "w") as f:
        json.dump(logic, f, indent=2)

    # 💾 Scriem intersecțiile (grupările)
    with open(output_json + ".intersections.json", "w") as f:
        json.dump(intersections, f, indent=2)


def update_phases_from_json(xml_path, update_json_path):
    if not os.path.exists(update_json_path + ".ttl.update.json"):
        print("[INFO] No update file found. Skipping update.")
        return
    tree = ET.parse(xml_path+".net.xml")
    root = tree.getroot()

    with open(update_json_path + ".ttl.update.json", "r") as f:
        updates = json.load(f)

    updated = []
    skipped = []

    for tlLogic in root.findall("tlLogic"):
        tls_id = tlLogic.get("id")
        if tls_id in updates:
            new_phases = updates[tls_id]["phases"]

            old_phases = tlLogic.findall("phase")
            if not old_phases:
                skipped.append(tls_id)
                continue

            expected_len = len(old_phases[0].get("state"))

            valid = all(len(p["state"]) == expected_len for p in new_phases)
            if not valid:
                skipped.append(tls_id)
                continue

            for p in old_phases:
                tlLogic.remove(p)

            for phase in new_phases:
                ET.SubElement(tlLogic, "phase",
                              duration=str(phase["duration"]),
                              state=phase["state"])

            updated.append(tls_id)

    tree.write(xml_path + ".net.xml")

def get_tls_phase_config(sumocfg_path):
    if traci.isLoaded():
        traci.close()

    traci.start(["sumo", "-c", sumocfg_path + ".sumocfg", "--start"])
    tls_ids = traci.trafficlight.getIDList()
    tls_phase_config = {}

    for tls_id in tls_ids:
        logic = traci.trafficlight.getAllProgramLogics(tls_id)[0]
        tls_phase_config[tls_id] = len(logic.getPhases())

    traci.close()
    return tls_phase_config

def get_tls_phase_config2():
    if not traci.isLoaded():
        exit("[ERROR] traci is already loaded. Close it before starting a new simulation.")

    tls_ids = traci.trafficlight.getIDList()
    tls_phase_config = {}

    for tls_id in tls_ids:
        logic = traci.trafficlight.getAllProgramLogics(tls_id)[0]
        tls_phase_config[tls_id] = len(logic.getPhases())

    return tls_phase_config

def extract_phases_from_json(json_path):
    return_vector = []
    with open(json_path + ".ttl.json", "r") as f:
        data = json.load(f)
        for tls_id, tls_data in data.items():
            for phase in tls_data["phases"]:
                return_vector.append(phase["duration"])
    return return_vector

def get_possible_states(json_path, tls_ids):
    with open(json_path + ".ttl.json", "r") as f:
        data = json.load(f)
    
    phases = {}
    for tls_id in tls_ids:
        if tls_id in data:
            phases[tls_id] = [phase["state"] for phase in data[tls_id]["phases"]]   
        else:
            phases[tls_id] = []
    return phases   

def get_min_duration(json_path, tls_ids):
    min_duration = float('inf')
    with open(json_path + ".ttl.json", "r") as f:
        data = json.load(f)
        for tls_id in tls_ids:
            if tls_id in data:
                for phase in data[tls_id]["phases"]:
                    min_duration = min(min_duration, phase["duration"])
    return min_duration if min_duration != float('inf') else 0

def get_main_and_sec(net_file, tls_ids):
    net = readNet(net_file + ".net.xml")
    mains = {}
    sec = {}

    for tls in tls_ids:
        node = net.getNode(tls)
        incoming_edges = list(node.getIncoming())
        incoming_edges.sort(key=lambda edge: edge.getLaneNumber(), reverse=True)
        mains[tls] = [edge.getID() for edge in incoming_edges[:2]]
        sec[tls] = [edge.getID() for edge in incoming_edges[2:]]
        # Store mains and sec in a dictionary variable
    traffic_lights_main_sec = {tls: {"main": mains[tls], 'sec': sec[tls]} for tls in tls_ids}
# eroare la secondary
    return traffic_lights_main_sec

def get_sim_cars(rou_file):
    tree = ET.parse(rou_file + ".rou.xml")
    root = tree.getroot()
    vehicles = []
    for vehicle in root.findall("trip"):
        vehicles.append(vehicle.get("id"))
    return len(vehicles)

def copy_jsons(json_path, output_path):
    dst = f"{output_path}.ttl.json"
    src = f"{json_path}.ttl.update.json"
    if os.path.exists(src):
        with open(src, "r") as f:
            data = json.load(f)
        with open(dst, "w") as f:
            json.dump(data, f, indent=2)
    else:
        print(f"[WARNING] {src} does not exist. Skipping copy.")


def json_copy(json_path, output_path):
    dst = f"{output_path}"
    src = f"{json_path}"
    if os.path.exists(src):
        with open(src, "r") as f:
            data = json.load(f)
        with open(dst, "w") as f:
            json.dump(data, f, indent=2)
    else:
        print(f"[WARNING] {src} does not exist. Skipping copy.")