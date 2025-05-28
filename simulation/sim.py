import simpy
from db.models import NodeRes, Resource
from simulation.types import SimulationRes
from simulation.topological_sort import get_sorted_node_ids

def get_events_list(nodes: [], relations: []) -> list:
    """Возвращает список событий"""
    events_list = []
    #выполняем топологическую сортировку узлов по связям между ними
    sorted_node_ids = get_sorted_node_ids(relations)

    # создаем словарь для быстрого доступа к узлам по ID
    node_dict = {node.id: node for node in nodes}

    # формируем новый список в нужном порядке
    for node_id in sorted_node_ids:
        if node_id in node_dict:
            events_list.append(node_dict[node_id])
    return events_list

cost = 0
report = []
simulation_res_table = []
table_for_export = []
current_res_values = {}

def set_resource_value_in_limits(new_val, min_val, max_val):
    """Устанавливает значение ресурса в заданных пределах"""
    if new_val < min_val:
        return min_val
    if new_val > max_val:
        return max_val
    return new_val

def add_resources_to_export_table(time: float):
    """Добавляет данные ресурсов в таблицу для экспорта"""
    global current_res_values, table_for_export

    sys_name_headers = table_for_export[1]
    sim_values_now = [current_res_values[sys_name]['current_value'] for sys_name in sys_name_headers if sys_name != 't']
    sim_values_now.insert(0, time)

    table_for_export.append(sim_values_now)

def do_math_operation_on_res(first_value: float, current_value: float, math_operation: str, min_value: float, max_value: float):
    """Выполняет математическую операцию над ресурсом"""
    coefficient = float(math_operation[1:])

    if math_operation[0] == "+" or math_operation[0] == "-":
        current_value = set_resource_value_in_limits(
            first_value + float(math_operation), min_value,  max_value)

    elif math_operation[0] == "/":
        current_value = set_resource_value_in_limits(
            first_value / coefficient, min_value, max_value)

    elif math_operation[0] == "*":
        current_value = set_resource_value_in_limits(
            first_value * coefficient,  min_value, max_value)

    return current_value

def change_resources(node_resources: [NodeRes], time: float):
    """Изменяет ресурсы в рамках одного этапа симуляции"""
    global current_res_values, simulation_res_table
    for res in node_resources:
        formula_parts = res.value.split(":=")
        sys_name = formula_parts[0]
        formula = formula_parts[1].translate(str.maketrans({'+': ' ', '-': ' ', '*': ' ', '/': ' '})).split()
        other_res_sys_name = formula[0]
        math_operation = formula_parts[1].removeprefix(other_res_sys_name)
        last_sys_name = math_operation[1:]

        is_last_res_sys_name = last_sys_name[1:4] == "Res"

        if is_last_res_sys_name and last_sys_name in current_res_values:
            math_operation = math_operation[0] + str(current_res_values[last_sys_name]['current_value'])


        if (sys_name not in current_res_values) or (other_res_sys_name not in current_res_values) or (is_last_res_sys_name and last_sys_name not in current_res_values):
            if sys_name not in current_res_values:
                report.append(f"ОШИБКА! Ресурс '{sys_name}' не опознан в формуле {res.value}")
            if other_res_sys_name not in current_res_values:
                report.append(f"ОШИБКА! Ресурс '{other_res_sys_name}' не опознан в формуле {res.value}")
            if last_sys_name not in current_res_values:
                report.append(f"ОШИБКА! Ресурс '{last_sys_name}' не опознан в формуле {res.value}")
        else:
            current_res = current_res_values[sys_name]

            report.append(f"Выполняется операция {math_operation} над ресурсом {sys_name} '{current_res['name']}'...")

            report.append(f"Текущее значение ресурса {current_res['name']}: {current_res['current_value']}")

            current_res['current_value'] = do_math_operation_on_res(
                current_res_values[other_res_sys_name]['current_value'],
                current_res['current_value'],
                math_operation,
                current_res['min_value'],
                current_res['max_value']
            )

            simulation_res_table.append(SimulationRes(id=current_res['id'], sys_name=sys_name, time=time,
                                                          name=current_res['name'],
                                                      value=current_res['current_value']))
            report.append(f"Новое значение ресурса {current_res['name']}: {current_res['current_value']}")

            add_resources_to_export_table(time)

def change_resources_out(node_resources_out: [NodeRes], env, duration, name):
    """Изменяет ресурсы на выходе"""
    global report
    yield env.timeout(duration)
    if len(node_resources_out) > 0:
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

def set_export_table_headers(sub_area_resources: [Resource]):
    """Устанавливает заголовки в таблицу для экспорта"""
    global table_for_export

    #названия ресурсов
    export_names = [sub_area.name for sub_area in sub_area_resources]
    export_names.insert(0, 'Время имитации')

    #системные имена ресурсов
    export_sys_names = [sub_area.sys_name for sub_area in sub_area_resources]
    export_sys_names.insert(0, 't')

    table_for_export.append(export_names)
    table_for_export.append(export_sys_names)

def fill_current_res_values_dict(sub_area_resources: [Resource]):
    """Заполняет словарь текущих значений ресурсов ПО
    для хранения информации об изменениях на входе/выходе"""
    global current_res_values
    res_values_list = [{'sys_name': res.sys_name,
                        'id': res.id,
                        'name': res.name,
                        'current_value': res.current_value,
                        'min_value': res.min_value,
                        'max_value': res.max_value}
                       for res in sub_area_resources]

    # формируем словарь, где ключ - системное имя ресурса
    current_res_values = {res['sys_name']: res for res in res_values_list}

def get_report(events: [], time_limit: int, sub_area_resources: [Resource]):
    """Возвращает отчет по симуляции"""
    global report, current_res_values, simulation_res_table, table_for_export
    #очищаем предыдущие результаты эксперимента
    report.clear()
    simulation_res_table.clear()
    table_for_export.clear()

    #заполняем словарь для хранения текущих значений ресурсов во время симуляции
    fill_current_res_values_dict(sub_area_resources)

    #устанавливаем заголовки в таблицу для дальнейшего экспорта в csv/xlsx
    set_export_table_headers(sub_area_resources)

    env = simpy.Environment()
    #запускаем симуляцию
    env.process(start(env, events))
    env.run(until=time_limit)
    report.append(f'Конец симуляции')
    report.append(f'Время симуляции - {time_limit}')
    report.append(f'Общие затраты: {cost}')
    return report, simulation_res_table, table_for_export