import subprocess
import os
from pathlib import Path
import shutil

randomTrips_path: Path = None

def init_randomTrips_path():
    global randomTrips_path
    randomTrips_path = "/usr/share/sumo/tools/randomTrips.py"


def write_run_script_sh(script_path: Path):
    """
    Generează un script .sh pentru iniţializare reţea + rute (compatibil Linux/Docker).
    """
    content = f"""#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 [path/to/city/CityName]"
  exit 1
fi

CITY_PATH="$1"
ORAS=$(basename "$CITY_PATH")

echo "[INFO] Convertim $ORAS.osm in $ORAS.net.xml..."
netconvert --osm-files "$CITY_PATH.osm" -o "$CITY_PATH.net.xml"

echo "[INFO] Simulam cu SUMO si generam fisierul $ORAS.sumocfg..."
sumo -n "$CITY_PATH.net.xml" -r "$CITY_PATH.rou.xml" --save-configuration "$CITY_PATH.sumocfg"

echo "[SUCCES] Procesul s-a finalizat pentru orasul: $ORAS"
"""
    script_path.write_text(content, encoding="utf-8")
    os.chmod(script_path, 0o755)
    print(f"[INFO] Script generat: {script_path}")

def run_scripts(city_path: str):
    city = Path(city_path)
    script = city.parent / f"{city.name}_run_scripts.sh"
    write_run_script_sh(script)
    print(f"[INFO] Rulez {script} pentru {city_path}...")
    res = subprocess.run([str(script), city_path], capture_output=True, text=True)
    print(res.stdout)
    print(res.stderr)
    if res.returncode != 0:
        raise RuntimeError(f"[ERROR] Scriptul a eșuat cu cod {res.returncode}")
