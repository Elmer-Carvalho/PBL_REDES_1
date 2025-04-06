from handlers import auth
from handlers import start
from server import bootstrap

datas = bootstrap.initialize_datas()
start_manager = start.StartManager(car_models=datas["car_models"], station_models=datas["station_models"])

handlers = {
    "START": start_manager.handle_start,
    "LOGIN": auth.login,
    "NAVIGATION": ...,
    "SELECTION_STATION": ...,
    "PAYMENT": ...
}

required_fields = ["type", "data", "status", "timestamp"]

def route_request(request: dict) -> bool:
    if validate_request(request, required_fields):
        #### 
        
        #Falta a validação do formato dos dados

        ####
        if request["type"] in handlers:
            return handlers[request["type"]](request)

def validate_request(data, required_fields):
    return all(field in data for field in required_fields)


