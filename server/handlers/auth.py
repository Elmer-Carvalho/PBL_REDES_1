import os
import json
import hashlib
from utils.time_utils import get_current_timestamp

class UserManager:
    def __init__(self, users_dir="data/users", car_models_file="data/car_models.json"):
        self.users_dir = users_dir
        self.car_models_file = car_models_file
        self.car_models = self.load_car_models()
        os.makedirs(users_dir, exist_ok=True)

    def load_car_models(self):
        """Carrega os modelos de carros do arquivo JSON."""
        if not os.path.exists(self.car_models_file):
            raise FileNotFoundError(f"Arquivo de modelos de carros {self.car_models_file} não encontrado")
        with open(self.car_models_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_user_filepath(self, username):
        """Gera o filepath a partir do hash do username."""
        user_hash = hashlib.sha256(username.encode()).hexdigest()
        return os.path.join(self.users_dir, f"{user_hash}.json")

    def register(self, request):
        data = request["data"]["content"]
        username = data.get("username")
        password = data.get("password")
        car_model = data.get("car_model")

        if not all([username, password, car_model]):
            return {
                "type": "register",
                "request_id": request["request_id"],
                "data": {},
                "status": {"code": 1, "message": "Campos obrigatórios ausentes"},
                "timestamp": get_current_timestamp()
            }
        
        if car_model not in self.car_models:
            return {
                "type": "register",
                "request_id": request["request_id"],
                "data": {},
                "status": {"code": 1, "message": "Modelo de carro inválido"},
                "timestamp": get_current_timestamp()
            }

        filepath = self.get_user_filepath(username)
        if os.path.exists(filepath):
            return {
                "type": "register",
                "request_id": request["request_id"],
                "data": {},
                "status": {"code": 1, "message": "Usuário já existe"},
                "timestamp": get_current_timestamp()
            }

        car_id = f"{car_model[:3].upper()}{hashlib.sha256(username.encode()).hexdigest()[:3]}"
        car_data = self.car_models[car_model].copy()
        car_data["car_id"] = car_id
        user_data = {
            "username": username,
            "password_hash": hashlib.sha256(password.encode()).hexdigest(),
            "car": car_data
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=4)
        
        return {
            "type": "register",
            "request_id": request["request_id"],
            "data": {"car_id": car_id},
            "status": {"code": 0, "message": "Cadastro realizado com sucesso"},
            "timestamp": get_current_timestamp()
        }

    def login(self, request):
        data = request["data"]["content"]
        username = data.get("username")
        password = data.get("password")

        if not all([username, password]):
            return {
                "type": "login",
                "request_id": request["request_id"],
                "data": {},
                "status": {"code": 1, "message": "Campos obrigatórios ausentes"},
                "timestamp": get_current_timestamp()
            }

        filepath = self.get_user_filepath(username)
        if not os.path.exists(filepath):
            return {
                "type": "login",
                "request_id": request["request_id"],
                "data": {},
                "status": {"code": 1, "message": "Usuário não encontrado"},
                "timestamp": get_current_timestamp()
            }

        with open(filepath, "r", encoding="utf-8") as f:
            user = json.load(f)
        
        if user["password_hash"] == hashlib.sha256(password.encode()).hexdigest():
            return {
                "type": "login",
                "request_id": request["request_id"],
                "data": {"car_id": user["car"]["car_id"]},
                "status": {"code": 0, "message": "Login bem-sucedido"},
                "timestamp": get_current_timestamp()
            }
        return {
            "type": "login",
            "request_id": request["request_id"],
            "data": {},
            "status": {"code": 1, "message": "Senha incorreta"},
            "timestamp": get_current_timestamp()
        }

user_manager = UserManager()