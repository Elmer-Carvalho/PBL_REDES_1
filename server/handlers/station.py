import os
import json
import threading
from models.electric_car import ElectricCar
from utils.time_utils import get_current_timestamp

class StationManager:
    def __init__(self, users_dir="data/users", stations_dir="data/stations"):
        """Inicializa com diretórios de usuários e postos, e locks por posto."""
        self.users_dir = users_dir
        self.stations_dir = stations_dir
        self.locks = {}  # Dicionário de locks por station_id

    def get_user_car(self, user_id):
        """Carrega o carro do usuário a partir do arquivo JSON."""
        filepath = os.path.join(self.users_dir, f"{user_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            user_data = json.load(f)
        car_data = user_data["user_car"]
        return ElectricCar(
            brand=car_data["brand"],
            model=car_data["model"],
            battery_capacity=car_data["battery_capacity"],
            energy_consumption=car_data["energy_consumption"],
            max_speed=car_data["max_speed"],
            current_battery=car_data["current_battery"]
        )

    def get_station_data(self, station_id):
        """Carrega os dados do posto a partir do arquivo JSON com lock."""
        filepath = os.path.join(self.stations_dir, f"{station_id}.json")
        if not os.path.exists(filepath):
            return None

        # Cria ou obtém o lock para este station_id
        if station_id not in self.locks:
            self.locks[station_id] = threading.Lock()
        lock = self.locks[station_id]

        # Adquire o lock e lê o arquivo
        with lock:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)

    def calculate_travel_time(self, car, distance):
        """Calcula o tempo de viagem em segundos (70% da velocidade máxima)."""
        speed = car.max_speed * 0.7  # km/h
        return (distance / speed) * 3600  # Convertido para segundos

    def calculate_charge_time(self, car):
        """Calcula o tempo de carregamento em segundos até 80% (50 kW padrão)."""
        charge_rate = 50  # kW (assumido, pode ser ajustado por posto)
        energy_needed = min(car.battery_capacity * 0.8 - car.current_battery, car.battery_capacity - car.current_battery)
        return (energy_needed / charge_rate) * 3600  # Segundos

    def handle_selection_station(self, request):
        """Seleciona o posto mais adequado com base no tempo total."""
        data = request["data"]
        user_id = data.get("user_id")
        list_stations = data.get("list_stations")

        # Validação dos campos
        if not user_id:
            return {
                "type": "SELECTION_STATION",
                "data": {
                    "user_id": user_id,
                    "id_station": None,
                    "price_loading": 0,
                    "message": "user_id ausente"
                },
                "status": {"code": 400, "message": "Erro na requisição"},
                "timestamp": get_current_timestamp()
            }

        if not list_stations or not isinstance(list_stations, dict):
            return {
                "type": "SELECTION_STATION",
                "data": {
                    "user_id": user_id,
                    "id_station": None,
                    "price_loading": 0,
                    "message": "list_stations ausente ou inválido"
                },
                "status": {"code": 400, "message": "Erro na requisição"},
                "timestamp": get_current_timestamp()
            }

        # Carrega o carro do usuário
        car = self.get_user_car(user_id)
        if not car:
            return {
                "type": "SELECTION_STATION",
                "data": {
                    "user_id": user_id,
                    "id_station": None,
                    "price_loading": 0,
                    "message": "Usuário não encontrado"
                },
                "status": {"code": 404, "message": "Usuário não encontrado"},
                "timestamp": get_current_timestamp()
            }

        # Calcula a autonomia atual para referência
        autonomy = car.current_range()

        # Avalia os postos
        viable_stations = []
        for station_id, station_info in list_stations.items():
            distance = station_info.get("distance_origin_position")
            try:
                distance = float(distance)
                if distance <= 0:
                    continue  # Ignora distâncias inválidas
            except (ValueError, TypeError):
                continue  # Ignora estações com distância inválida

            # Verifica se o carro pode chegar ao posto
            if not car.can_complete_trip(distance):
                continue

            # Carrega dados do posto com lock
            station_data = self.get_station_data(station_id)
            if not station_data:
                continue  # Ignora postos inexistentes

            # Calcula tempos
            travel_time = self.calculate_travel_time(car, distance)  # Segundos
            charge_time = self.calculate_charge_time(car)  # Segundos
            wait_time = 0

            # Verifica disponibilidade de vagas
            if station_data["available_slots"] == 0:
                # Calcula o tempo até a próxima vaga liberar
                min_time_to_finish = float("inf")
                current_time = get_current_timestamp(as_float=True)  # Timestamp em segundos
                for vehicle in station_data["vehicles"].values():
                    remaining_time = vehicle["estimated_timestamp"] - current_time
                    if remaining_time > 0:
                        min_time_to_finish = min(min_time_to_finish, remaining_time)
                if min_time_to_finish == float("inf"):
                    continue  # Nenhum veículo está carregando (erro nos dados)
                wait_time = max(0, min_time_to_finish - travel_time)

            total_time = travel_time + wait_time + charge_time
            viable_stations.append({
                "id": station_id,
                "distance": distance,
                "total_time": total_time,
                "travel_time": travel_time,
                "wait_time": wait_time,
                "charge_time": charge_time,
                "address": station_data.get("address", "Endereço não disponível")
            })

        if not viable_stations:
            return {
                "type": "SELECTION_STATION",
                "data": {
                    "user_id": user_id,
                    "id_station": None,
                    "price_loading": 0,
                    "message": f"Nenhum posto alcançável ou disponível encontrado. Autonomia atual: {autonomy:.2f} km"
                },
                "status": {"code": 200, "message": "Nenhum posto disponível"},
                "timestamp": get_current_timestamp()
            }

        # Escolhe o posto com menor tempo total
        best_station = min(viable_stations, key=lambda x: x["total_time"])
        price_loading = best_station["charge_time"] * 0.1  # Exemplo: 0.1 unidade por segundo
        travel_minutes = best_station["travel_time"] / 60

        return {
            "type": "SELECTION_STATION",
            "data": {
                "user_id": user_id,
                "id_station": best_station["id"],
                "price_loading": price_loading,
                "message": f"Posto recomendado: {best_station['address']}. Distância: {best_station['distance']} km, tempo estimado de chegada: {travel_minutes:.1f} minutos"
            },
            "status": {"code": 200, "message": "Sucesso"},
            "timestamp": get_current_timestamp()
        }
