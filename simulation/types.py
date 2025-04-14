from db.models import NodeRes

class SimulationRes:
    def __init__(self, id: int, name: str, sys_name: str, value: float):
        self.id = id
        self.name = name
        self.sys_name = sys_name
        self.value = value

class SimulationNodedata:
    def __init__(self, id: int, name: str, cost: int, duration: int, resources_in: [NodeRes], resources_out: [NodeRes]):
        self.id = id
        self.name = name
        self.cost = cost
        self.duration = duration
        self.db_resources_in = resources_in
        self.db_resources_out = resources_out