import simpy
from db.models import Relation, Node
def get_events_list(nodes: [], relations: []) -> list:
    """Возвращает список событий"""
    events_list = []
    relations.sort(key=lambda rel: rel.source_id)
    for relation in relations:
        print(relation.source_id, relation.target_id)
        node = next((node for node in nodes if node.id == relation.source_id), None)
        events_list.append(node)
        nodes.pop(nodes.index(node))
    events_list.append(nodes[0])
    return events_list

cost = 0
report = []

def start(env, events):
    """Запускает симуляцию"""
    global cost, report
    while True:
        for event in events:
            report.append(f'{event.name} - начало в {env.now}')
            cost += event.cost
            yield env.timeout(event.duration)


def get_report(events: [], time_limit: int):
    global report
    report.append(f'Время симуляции - {time_limit}')
    """Возвращает отчет по симуляции"""
    env = simpy.Environment()
    env.process(start(env, events))
    env.run(until=time_limit)
    report.append(f'Общие затраты: {cost}')
    return report