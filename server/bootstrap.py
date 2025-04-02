import os
import csv
import json

def check_and_create_stations(csv_file="server\\data\\feira_de_santana_stations.csv", output_folder="server\\data\\stations"):
    os.makedirs(output_folder, exist_ok=True)
    expected_ids = set()
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            expected_ids.add(int(row["id"]))
    
    existing_files = {int(f.split("_")[1].split(".")[0]) for f in os.listdir(output_folder) if f.startswith("station_") and f.endswith(".json")}
    missing_ids = expected_ids - existing_files
    
    if missing_ids:
        print(f"Arquivos faltantes detectados: {missing_ids}")
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                station_id = int(row["id"])
                if station_id in missing_ids:
                    station_data = {
                        "id": station_id,
                        "max_slots": int(row["quantidadeDeVeiculosSimultaneos"]),
                        "available_slots": int(row["quantidadeDeVeiculosSimultaneos"]),
                        "vehicles": {}
                    }
                    filepath = os.path.join(output_folder, f"station_{station_id}.json")
                    with open(filepath, "w", encoding="utf-8") as json_file:
                        json.dump(station_data, json_file, indent=4)
                    print(f"Recriado: {filepath}")
    else:
        print("Todos os arquivos das estações estão presentes.")


if __name__ == "__main__":
    check_and_create_stations()