class ElectricCar:
    def __init__(self, brand, model, battery_capacity, energy_consumption, max_speed, acceleration, car_id):
        # Validação básica dos parâmetros
        if battery_capacity < 0 or energy_consumption <= 0 or max_speed <= 0:
            raise ValueError("Capacidade, consumo e velocidade máxima devem ser positivos")
        if acceleration <= 0:
            raise ValueError("Aceleração deve ser positiva")

        self.brand = brand
        self.model = model
        self.battery_capacity = battery_capacity  # kWh
        self.energy_consumption = energy_consumption  # kWh/km
        self.max_speed = max_speed  # km/h
        self.acceleration = acceleration  # segundos para 0-100 km/h
        self.car_id = car_id

        self.current_battery = battery_capacity / 2  # kWh (inicia com 50% de carga)

        self.current_latitude = None
        self.current_longitude = None
        self.destination_latitude = None
        self.destination_longitude = None

    def current_range(self):
        """Retorna quantos KM são possíveis de serem rodados com a bateria atual"""
        return self.current_battery / self.energy_consumption

    def time_to_destination(self, distance):
        """Tempo estimado em segundos para chegar ao destino, dada uma distância em KM"""
        if distance < 0:
            raise ValueError("Distância deve ser não-negativa")
        
        # Velocidade média estimada (70% da velocidade máxima como realista)
        average_speed = self.max_speed * 0.7  # km/h
        time_hours = distance / average_speed  # horas
        return time_hours * 3600  # Convertendo para segundos

    def battery_at_destination(self, distance):
        """Estimates the remaining battery (kWh) after traveling a given distance in km"""
        if distance < 0:
            raise ValueError("Distância deve ser não-negativa")
        
        energy_used = distance * self.energy_consumption  # kWh consumidos
        remaining_battery = self.current_battery - energy_used
        return max(0, remaining_battery)  # Retorna 0 se bateria acabar

    def charge(self, energy_added):
        """Adds energy (kWh) to the battery, respecting capacity limit"""
        if energy_added < 0:
            raise ValueError("Energia adicionada deve ser não-negativa")
        self.current_battery = min(self.battery_capacity, self.current_battery + energy_added)

    def consume(self, distance):
        """Consumes energy based on distance traveled (km) and returns if battery remains"""
        if distance < 0:
            raise ValueError("Distância deve ser não-negativa")
        energy_used = distance * self.energy_consumption
        self.current_battery = max(0, self.current_battery - energy_used)
        return self.current_battery > 0  # Retorna False se bateria acabar

# Exemplo de uso
if __name__ == "__main__":
    # Criando um Tesla Model 3 como exemplo
    tesla = ElectricCar(
        brand="Tesla",
        model="Model 3",
        battery_capacity=75,  # kWh
        energy_consumption=0.15,  # kWh/km
        max_speed=261,  # km/h
        acceleration=3.1,  # segundos (0-100 km/h)
        car_id="TES001"
    )

    # Testando as funções
    distance = 100  # km
    print(f"Autonomia atual: {tesla.current_range():.2f} km")
    print(f"Tempo estimado para {distance} km: {tesla.time_to_destination(distance):.2f} segundos")
    print(f"Bateria ao chegar ({distance} km): {tesla.battery_at_destination(distance):.2f} kWh")
    print(f"Consumindo {distance} km...")
    tesla.consume(distance)
    print(f"Bateria atual após viagem: {tesla.current_battery:.2f} kWh")