class NodeData:
    """Используется только во время симуляции"""
    def __init__(self, id: int, name: str, cost: int, duration: int):
        self.id = id
        self.name = name
        self.cost = cost
        self.duration = duration