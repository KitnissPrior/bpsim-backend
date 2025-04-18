import simpy
from db.models import NodeRes, Resource
from simulation.types import SimulationRes
from simulation.topological_sort import get_sorted_node_ids

def get_events_list(nodes: [], relations: []) -> list:
    """Возвращает список событий"""
    events_list = []
    #выполняем топологическую сортировку узлов по связям между ними
    sorted_node_ids = get_sorted_node_ids(relations)
    # словарь для быстрого доступа к узлам по ID
    node_dict = {node.id: node for node in nodes}

    # формируем новый список в нужном порядке
    for node_id in sorted_node_ids:
        if node_id in node_dict:
            events_list.append(node_dict[node_id])
    return events_list

cost = 0
report = []
simulation_res_table = []
current_res_values = {}

def change_resources(node_resources: [NodeRes], time: float):
    global current_res_values, simulation_res_table
    for res in node_resources:
        formula_parts = res.value.split(":=")
        sys_name = formula_parts[0]
        formula = formula_parts[1].translate(str.maketrans({'+': ' ', '-': ' ', '*': ' ', '/': ' '})).split()
        other_res_sys_name = formula[0]
        math_operation = formula_parts[1].removeprefix(other_res_sys_name)
        current_res = current_res_values[sys_name]

        report.append(f"Выполняется операция {math_operation} над ресурсом {sys_name} '{current_res['name']}'...")

        report.append(f"Текущее значение ресурса {current_res['name']}: {current_res['value']}")
        coefficient = float(math_operation[1:])

        if math_operation[0] == "+" or math_operation[0] == "-":
            current_res['value'] = current_res_values[other_res_sys_name]['value'] + float(math_operation)
        elif math_operation[0] == "/":
            current_res['value'] = current_res_values[other_res_sys_name]['value'] / coefficient
        elif math_operation[0] == "*":
            current_res['value'] = current_res_values[other_res_sys_name]['value'] * coefficient

        simulation_res_table.append(SimulationRes(id=current_res['id'], sys_name=sys_name, time=time,
                                                      name=current_res['name'], value=current_res['value']))
        report.append(f"Новое значение ресурса {current_res['name']}: {current_res['value']}")

def change_resources_out(node_resources_out: [NodeRes], env, duration, name):
    global report
    yield env.timeout(duration)
    change_resources(node_resources_out, env.now)
    report.append(f'{name} - окончание в {env.now}')

def start(env, events):
    """Запускает симуляцию"""
    global cost, report
    while True:
        for event in events:
            time_start = env.now
            report.append(f'{event.name} - начало в {time_start}')
            if len(event.db_resources_in) > 0:
                change_resources(event.db_resources_in, time_start)
            cost += event.cost
            yield env.process(change_resources_out(event.db_resources_out, env, event.duration, event.name))
            report.append(" ")


def get_report(events: [], time_limit: int, sub_area_resources: [Resource]):
    """Возвращает отчет по симуляции"""
    global report, current_res_values, simulation_res_table
    #очищаем предыдущие результаты эксперимента
    report.clear()
    simulation_res_table.clear()
    #формируем словарь текущих значений ресурсов ПО для хранения информации об изменениях на входе/выходе;
    #ключ - системное имя ресурса
    res_values_list = [{'sys_name': res.sys_name, 'id': res.id,
                        'name': res.name, 'value': res.current_value}
                       for res in sub_area_resources]
    current_res_values = {res['sys_name']: res for res in res_values_list}

    env = simpy.Environment()
    #запускаем симуляцию
    env.process(start(env, events))
    env.run(until=time_limit)
    report.append(f'Конец симуляции')
    report.append(f'Время симуляции - {time_limit}')
    report.append(f'Общие затраты: {cost}')
    for row in simulation_res_table:
        print(row.sys_name, row.value)
    return report, simulation_res_table