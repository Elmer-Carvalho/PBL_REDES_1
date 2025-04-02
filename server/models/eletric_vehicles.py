class ElectricCar:
    def __init__(self, brand, model, battery_capacity, current_battery, energy_consumption, max_speed, car_id):
        """Inicializa um carro elétrico com suas propriedades e estado inicial."""
        if battery_capacity < 0 or energy_consumption <= 0 or max_speed <= 0:
            raise ValueError("Capacidade, consumo e velocidade máxima devem ser positivos")
        if current_battery < 0 or current_battery > battery_capacity:
            raise ValueError("Bateria atual deve estar entre 0 e a capacidade máxima")

        self.brand = brand
        self.model = model
        self.battery_capacity = battery_capacity  # kWh (máxima)
        self.current_battery = current_battery    # kWh (atual)
        self.energy_consumption = energy_consumption  # kWh/km
        self.max_speed = max_speed  # km/h
        self.car_id = car_id

    def current_range(self):
        """Retorna a autonomia atual em km com base na bateria atual."""
        return self.current_battery / self.energy_consumption

    def battery_at_destination(self, distance):
        """Estima a bateria restante (kWh) após percorrer uma distância em km."""
        if distance < 0:
            raise ValueError("Distância deve ser não-negativa")
        energy_used = distance * self.energy_consumption
        return max(0, self.current_battery - energy_used)

    def can_complete_trip(self, distance):
        """Verifica se o carro pode completar o percurso com a bateria atual."""
        if distance < 0:
            raise ValueError("Distância deve ser não-negativa")
        return self.battery_at_destination(distance) > 0

    def charge(self, energy_added):
        """Adiciona energia (kWh) à bateria, respeitando o limite da capacidade."""
        if energy_added < 0:
            raise ValueError("Energia adicionada deve ser não-negativa")
        self.current_battery = min(self.battery_capacity, self.current_battery + energy_added)

    def consume(self, distance):
        """Consome energia com base na distância percorrida (km) e retorna se resta bateria."""
        if distance < 0:
            raise ValueError("Distância deve ser não-negativa")
        energy_used = distance * self.energy_consumption
        self.current_battery = max(0, self.current_battery - energy_used)
        return self.current_battery > 0
        