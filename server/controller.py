import json
from handlers.auth import AuthManager
from handlers.start import StartManager
from handlers.trip import TripManager
from handlers.station import StationManager
from utils.time_utils import get_current_timestamp
import bootstrap

# Carrega dados na inicialização
bootstrap.check_and_create_stations()
data = bootstrap.initialize_data()
start_manager = StartManager(car_models=data["car_models"], station_models=data["station_models"])
auth_manager = AuthManager(car_models=data["car_models"])
trip_manager = TripManager()
station_manager = StationManager()

handlers = {
    "START": start_manager.handle_start,
    "LOGIN": auth_manager.handle_login,
    "NAVIGATION": trip_manager.handle_navigation,
    "SELECTION_STATION": station_manager.handle_selection_station,
    "PAYMENT": station_manager.handle_payment
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
    # Lista de requisições para teste
    test_requests = [
        # 1. START: Obter dados iniciais
        {
            "type": "START",
            "data": {},
            "status": {"code": 200, "message": "Sucesso"},
            "timestamp": "2025-03-29T10:30:46Z"
        },
        # 2. LOGIN: Criar um usuário
        {
            "type": "LOGIN",
            "data": {
                "user_name": "joao",
                "selected_car": "Tesla Model 3",
                "battery_car": 75
            },
            "status": {"code": 200, "message": "Sucesso"},
            "timestamp": "2025-03-29T10:30:46Z"
        },
        # 3. NAVIGATION: Verificar autonomia para 300 km
        {
            "type": "NAVIGATION",
            "data": {
                "user_id": None,  # Será preenchido com o user_id do LOGIN
                "route_distance": 300
            },
            "status": {"code": 200, "message": "Sucesso"},
            "timestamp": "2025-03-29T10:30:46Z"
        },
        # 4. SELECTION_STATION: Selecionar um posto
        {
            "type": "SELECTION_STATION",
            "data": {
                "user_id": None,  # Será preenchido com o user_id do LOGIN
                "list_stations": {
                    "1": {"distance_origin_position": 50},
                    "2": {"distance_origin_position": 30}
                }
            },
            "status": {"code": 200, "message": "Sucesso"},
            "timestamp": "2025-03-29T10:30:46Z"
        },
        # 5. PAYMENT: Confirmar pagamento e reservar vaga
        {
            "type": "PAYMENT",
            "data": {
                "user_id": None,  # Será preenchido com o user_id do LOGIN
                "id_station": None,  # Será preenchido com o id_station do SELECTION_STATION
                "confirmation": True
            },
            "status": {"code": 200, "message": "Sucesso"},
            "timestamp": "2025-03-29T10:30:46Z"
        },
        # 6. PAYMENT: Não confirmar pagamento (deleta usuário)
        {
            "type": "PAYMENT",
            "data": {
                "user_id": None,  # Será preenchido com um novo user_id do LOGIN
                "id_station": "1",
                "confirmation": False
            },
            "status": {"code": 200, "message": "Sucesso"},
            "timestamp": "2025-03-29T10:30:46Z"
        }
    ]

    print("=== Iniciando Teste de Requisições ===")
    user_id = None
    station_id = None

    # Executa cada requisição em sequência
    for i, request in enumerate(test_requests, 1):
        print(f"\nTeste {i}: {request['type']}")

        # Preenche user_id e id_station dinamicamente
        if request["type"] in ["NAVIGATION", "SELECTION_STATION", "PAYMENT"] and user_id:
            request["data"]["user_id"] = user_id
        if request["type"] == "PAYMENT" and station_id and request["data"]["confirmation"]:
            request["data"]["id_station"] = station_id

        # Executa a requisição
        response = route_request(request)
        print(json.dumps(response, indent=4))

        # Armazena user_id do LOGIN e id_station do SELECTION_STATION
        if request["type"] == "LOGIN" and response["status"]["code"] == 200:
            user_id = response["data"]["user_id"]
            print(f"User ID gerado: {user_id}")
        if request["type"] == "SELECTION_STATION" and response["status"]["code"] == 200:
            station_id = response["data"]["id_station"]
            print(f"Station ID selecionado: {station_id}")

        # Cria um novo usuário para o teste de PAYMENT com confirmation=False
        if request["type"] == "PAYMENT" and not request["data"]["confirmation"]:
            # Faz um novo LOGIN para gerar um novo user_id
            new_login = {
                "type": "LOGIN",
                "data": {
                    "user_name": "maria",
                    "selected_car": "Tesla Model 3",
                    "battery_car": 50
                },
                "status": {"code": 200, "message": "Sucesso"},
                "timestamp": "2025-03-29T10:30:46Z"
            }
            new_response = route_request(new_login)
            print("\nNovo LOGIN para teste de deleção:")
            print(json.dumps(new_response, indent=4))
            if new_response["status"]["code"] == 200:
                request["data"]["user_id"] = new_response["data"]["user_id"]
                print(f"Novo User ID gerado para deleção: {request['data']['user_id']}")
            response = route_request(request)  # Re-executa o PAYMENT com o novo user_id
            print(json.dumps(response, indent=4))

    print("\n=== Teste Concluído ===")