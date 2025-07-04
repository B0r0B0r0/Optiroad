import random


def sort_edges_by_exited(edges_dict):
    sorted_edges = list(edges_dict.items())
    for i in range(len(sorted_edges)):
        for j in range(i + 1, len(sorted_edges)):
            if sorted_edges[j][1]["exited"] > sorted_edges[i][1]["exited"]:
                sorted_edges[i], sorted_edges[j] = sorted_edges[j], sorted_edges[i]
    return sorted_edges

def sort_edges_by_entered(edges_dict):
    sorted_edges = list(edges_dict.items())
    for i in range(len(sorted_edges)):
        for j in range(i + 1, len(sorted_edges)):
            if len(sorted_edges[j][1]["entered"]) > len(sorted_edges[i][1]["entered"]):
                sorted_edges[i], sorted_edges[j] = sorted_edges[j], sorted_edges[i]
    return sorted_edges

def get_available_exits(current_edge, edges):
    available = []
    for edge_id, info in edges.items():
        if edge_id != current_edge and info["exited"] > 0:
            available.append(edge_id)
    return available

def generate_rou_file(data):
    edges = data["edges"]

    vehicle_id = 0
    trips = []

    total_entered = sum(len(info["entered"]) for info in edges.values())
    total_exited = sum(info["exited"] for info in edges.values())

    num_trips_target = max(total_entered, total_exited)


    delta_entered = num_trips_target - total_entered
    if delta_entered > 0:
        sorted_edges = sort_edges_by_entered(edges)
        i = 0
        while delta_entered > 0 and sorted_edges:
            edge_id, info = sorted_edges[i % len(sorted_edges)]
            last_time = info["entered"][-1] if info["entered"] else 0
            new_time = float(int(last_time) + random.randint(1, 5))
            new_time = new_time % 3600
            info["entered"].append(new_time)
            delta_entered -= 1
            i += 1


    delta_exited = num_trips_target - total_exited
    if delta_exited > 0:
        sorted_edges = sort_edges_by_exited(edges)
        i = 0
        while delta_exited > 0 and sorted_edges:
            edge_id, info = sorted_edges[i % len(sorted_edges)]
            info["exited"] += 1
            delta_exited -= 1
            i += 1


    all_entered = []
    for edge_id, info in edges.items():
        for timestamp in info["entered"]:
            all_entered.append( (timestamp, edge_id) )
    all_entered.sort()

    all_exits = []
    for edge_id, info in edges.items():
        all_exits.extend([edge_id] * info["exited"])
    random.shuffle(all_exits)

    for i in range(num_trips_target):
        depart_time, from_edge = all_entered[i]
        to_edge = all_exits[i]

        if from_edge == to_edge:
            other_options = [e for e in all_exits if e != from_edge]
            if other_options:
                to_edge = random.choice(other_options)

        trips.append({
            "id": f"veh{vehicle_id}",
            "depart": f"{depart_time:.2f}",
            "from": from_edge,
            "to": to_edge
        })
        vehicle_id += 1

    trips.sort(key=lambda trip: float(trip["depart"]))

    trips_xml = '<trips>\n'
    for trip in trips:
        trips_xml += f'    <trip id="{trip["id"]}" depart="{trip["depart"]}" from="{trip["from"]}" to="{trip["to"]}"/>\n'
    trips_xml += '</trips>\n'

    return trips_xml

def aggregate_rsu_events(events_list):
    """
    Aggregates multiple RSU event documents into a single dict per RSU.
    - Concatenates all 'entered' lists and sorts them.
    - Sums all 'exited' counts.
    """

    aggregated = {}

    for event in events_list:
        rsu_id = event.get("rsu_id")
        if rsu_id is None:
            continue

        entered_list = event.get("entered", [])
        exited_count = event.get("exited", 0)

        if rsu_id not in aggregated:
            aggregated[rsu_id] = {
                "entered": [],
                "exited": 0
            }

        aggregated[rsu_id]["entered"].extend(entered_list)
        aggregated[rsu_id]["exited"] += exited_count

    # Sort entered lists
    for rsu in aggregated.values():
        rsu["entered"].sort()
    to_return = {"edges": aggregated}
    return to_return

