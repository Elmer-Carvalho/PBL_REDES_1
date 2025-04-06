import json
from handlers import auth, start, trip, station
from utils.time_utils import get_current_timestamp
import bootstrap

datas = bootstrap.initialize_datas()
start_manager = start.StartManager(car_models=datas["car_models"], station_models=datas["station_models"])
auth_manager = auth.AuthManager(car_models=datas["car_models"])
trip_manager = trip.TripManager()
station_manager = station.StationManager()

handlers = {
    "START": start_manager.handle_start,
    "LOGIN": auth_manager.handle_login,
    "NAVIGATION": trip_manager.handle_navigation,
    "SELECTION_STATION": station_manager.handle_selection_station,
    "PAYMENT": ...
}

required_fields = ["type", "data", "status", "timestamp"]

def route_request(request: dict) -> dict:
    if not validate_request(request, required_fields):
        return {
            "type": request.get("type", "error"),
            "data": {},
            "status": {"code": 400, "message": "Campos obrigatórios ausentes"},
            "timestamp": get_current_timestamp()
        }

    if request["type"] in handlers:
        return handlers[request["type"]](request)

    return {
        "type": request.get("type", "error"),
        "data": {},
        "status": {"code": 404, "message": "Ação desconhecida"},
        "timestamp": get_current_timestamp()
    }

def validate_request(data, required_fields):
    return all(field in data for field in required_fields)

if __name__ == "__main__":
    request = {
        "type": "LOGIN",
        "data": {
            "user_name": "joao",
            "selected_car": "Tesla Model 3",
            "battery_car": 75
        },
        "status": {"code": 200, "message": "Sucesso"},
        "timestamp": "2025-03-29T10:30:46Z"
    }
    response = route_request(request)
    print(json.dumps(response, indent=4))


