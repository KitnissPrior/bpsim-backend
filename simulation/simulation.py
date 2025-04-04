import re

import simpy
from db.models import NodeRes, Resource
from simulation.types import SimulationRes


def get_events_list(nodes: [], relations: []) -> list:
    """Возвращает список событий"""
    events_list = []
    relations.sort(key=lambda rel: rel.source_id)
    for relation in relations:
        node = next((node for node in nodes if node.id == relation.source_id), None)
        events_list.append(node)
        nodes.pop(nodes.index(node))
    events_list.append(nodes[0])
    return events_list

cost = 0
report = []
simulation_res_table = [SimulationRes]
current_res_values = {}

def change_resources(node_resources: [NodeRes]):
    global current_res_values, simulation_res_table
    for res in node_resources:
        formula_parts = res.value.split(":=")
        sys_name = formula_parts[0]
        formula = formula_parts[1].translate(str.maketrans({'+': ' ', '-': ' ', '*': ' ', '/': ' '})).split()
        other_res_sys_name = formula[0]
        math_operation = formula_parts[1].removeprefix(other_res_sys_name)
        current_res = current_res_values[sys_name]

        report.append(f"Выполняется операция {math_operation} над ресурсом {sys_name} '{current_res['name']}'")

        report.append(f"Текущее значение ресурса {current_res['name']}: {current_res['value']}")
        coefficient = float(math_operation[1:])

        if math_operation[0] == "+" or math_operation[0] == "-":
            current_res['value'] = current_res_values[other_res_sys_name]['value'] + float(math_operation)
        elif math_operation[0] == "/":
            current_res['value'] = current_res_values[other_res_sys_name]['value'] / coefficient
        elif math_operation[0] == "*":
            current_res['value'] = current_res_values[other_res_sys_name]['value'] * coefficient

        simulation_res_table.append(SimulationRes(id=current_res['id'], sys_name=sys_name,
                                                      name=current_res['name'], value=current_res['value']))
        report.append(f"Новое значение ресурса {current_res['name']}: {current_res['value']}")
        report.append(" ")

def change_resources_out(node_resources_out: [NodeRes], env, duration, name):
    global report
    change_resources(node_resources_out)
    report.append(f'{name} - окончание в {env.now}')
    yield env.timeout(duration)




def start(env, events):
    """Запускает симуляцию"""
    global cost, report
    while True:
        for event in events:
            report.append(f'{event.name} - начало в {env.now}')
            if len(event.db_resources_in) > 0:
                change_resources(event.db_resources_in)
            cost += event.cost
            #yield env.process(change_resources_out(event.db_resources_out, env, event.duration, event.name))
            yield env.timeout(event.duration)


def get_report(events: [], time_limit: int, sub_area_resources: [Resource]):
    """Возвращает отчет по симуляции"""
    global report, current_res_values
    #очищаем предыдущие результаты эксперимента
    report.clear()
    #формируем словарь текущих значений ресурсов ПО для хранения информации об изменениях на входе/выходе
    #ключ - id ресурса
    res_values_list = [{'sys_name': res.sys_name, 'id': res.id,
                        'name': res.name, 'value': res.current_value}
                       for res in sub_area_resources]
    current_res_values = {res['sys_name']: res for res in res_values_list}

    report.append(f'Время симуляции - {time_limit}')
    env = simpy.Environment()
    #запускаем симуляцию
    env.process(start(env, events))
    env.run(until=time_limit)
    report.append(f'Конец симуляции')
    report.append(f'Общие затраты: {cost}')
    return report