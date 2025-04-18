from collections import defaultdict


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.vertices = set()

    def add_edge(self, u, v):
        """Добавление ребра в граф"""
        self.graph[u].append(v)
        self.vertices.add(u)
        self.vertices.add(v)

    def topological_sort(self):
        """
        Выполняет топологическую сортировку линейного графа
        """
        # Список для хранения результата
        result = []
        # Отметки посещения вершин
        visited = {v: False for v in self.vertices}

        def dfs_util(v):
            visited[v] = True

            # Рекурсия для всех смежных вершин
            for i in self.graph[v]:
                if not visited[i]:
                    dfs_util(i)

            # Добавляем вершину в результат
            result.append(v)

        # Выполняем DFS только для используемых вершин
        for v in self.vertices:
            if not visited[v]:
                dfs_util(v)

        # Получаем правильный порядок (реверсируем список)
        result.reverse()
        return result

def create_graph(relations: []):
    """Создает из списка связей модели линейный граф"""
    # Создаём граф и добавляем рёбра
    graph = Graph()
    edges = [(relation.source_id, relation.target_id) for relation in relations]
    for u, v in edges:
        graph.add_edge(u, v)
    return graph

def get_sorted_node_ids(relations: []):
    """Возвращает отсортированный список id узлов"""
    graph = create_graph(relations)
    return graph.topological_sort()