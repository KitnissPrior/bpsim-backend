import simpy
def get_events_list(nodes: list[Node], relations: list[Relation]) -> list:
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
report = list[str]
report.append('Время симуляции - 100')
def start(env, events):
    global cost, report
    while True:
        for event in events:
            report.append(f'{event.name} - начало в %d' % env.now)
            cost += event.cost
            yield env.timeout(event.duration)


env = simpy.Environment()

#events = get_events_list(nodes, relations)
#env.process(start(env, events))
#env.run(until=100)