import os
import xml.etree.ElementTree as ET

def replace_tls_ids_with_edges(rou_file_path):
    """
    Parses .net.xml in same folder.
    For each TLS ID in .rou.xml, maps to incoming/outgoing edge IDs
    based on edge 'to' and 'from' attributes.
    Rewrites the .rou.xml in place with edge IDs.
    """
    sumo_folder = os.path.dirname(rou_file_path)

    # 1️⃣ Find .net.xml
    net_files = [f for f in os.listdir(sumo_folder) if f.endswith(".net.xml")]
    if not net_files:
        raise FileNotFoundError("No .net.xml file found in SUMO folder")
    net_file_path = os.path.join(sumo_folder, net_files[0])
    print(f"[INFO] Using net file: {net_file_path}")

    # 2️⃣ Build mapping TLS_ID -> edges
    incoming_edges = {}
    outgoing_edges = {}

    net_tree = ET.parse(net_file_path)
    net_root = net_tree.getroot()

    for edge in net_root.findall(".//edge"):
        from_node = edge.get("from")
        to_node = edge.get("to")
        edge_id = edge.get("id")

        if to_node:
            incoming_edges.setdefault(to_node, []).append(edge_id)
        if from_node:
            outgoing_edges.setdefault(from_node, []).append(edge_id)

    print(f"[INFO] Parsed {len(incoming_edges)} incoming and {len(outgoing_edges)} outgoing mappings.")

    # 3️⃣ Load rou.xml
    rou_tree = ET.parse(rou_file_path)
    rou_root = rou_tree.getroot()

    for trip in rou_root.findall("trip"):
        from_tls = trip.get("from")
        to_tls = trip.get("to")

        from_candidates = outgoing_edges.get(from_tls) or incoming_edges.get(from_tls)
        to_candidates = incoming_edges.get(to_tls) or outgoing_edges.get(to_tls)

        if not from_candidates:
            print(f"[WARN] No edge mapping found for from={from_tls}. Removing trip.")
            rou_root.remove(trip)
            continue

        if not to_candidates:
            print(f"[WARN] No edge mapping found for to={to_tls}. Removing trip.")
            rou_root.remove(trip)
            continue

        trip.set("from", from_candidates[0])
        trip.set("to", to_candidates[0])

    # 4️⃣ Save
    rou_tree.write(rou_file_path)
    print(f"[SUCCESS] Rewrote {rou_file_path} with valid edge IDs")
