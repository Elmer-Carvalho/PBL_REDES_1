from handlers import auth

handlers = {
    ...
}

required_fields = ["type", "request_id", "data", "status", "timestamp"]

def route_request(request: dict) -> bool:
    if validate_request(request, required_fields):
        #### 
        
        #Falta a validação do formato dos dados

        ####
        if request["type"] in handlers:
            handlers[request["type"]](request)

def validate_request(data, required_fields):
    return all(field in data for field in required_fields)


