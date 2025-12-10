"""
Моделі даних для графів та результатів пошуку
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class Node:
    """Модель вершини графа"""
    
    def __init__(self, node_id: str, label: str, x: float = 0, y: float = 0):
        self.id = node_id
        self.label = label
        self.x = x
        self.y = y
    
    def to_dict(self) -> Dict:
        """Конвертація у словник"""
        return {
            'id': self.id,
            'label': self.label,
            'x': self.x,
            'y': self.y
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Node':
        """Створення з словника"""
        return Node(
            node_id=data['id'],
            label=data['label'],
            x=data.get('x', 0),
            y=data.get('y', 0)
        )


class Edge:
    """Модель ребра графа"""
    
    def __init__(self, from_node: str, to_node: str, weight: float):
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight
    
    def to_dict(self) -> Dict:
        """Конвертація у словник"""
        return {
            'from': self.from_node,
            'to': self.to_node,
            'weight': self.weight
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Edge':
        """Створення з словника"""
        return Edge(
            from_node=data['from'],
            to_node=data['to'],
            weight=data['weight']
        )


class Graph:
    """Модель графа"""
    
    def __init__(self, name: str, nodes: List[Node] = None, edges: List[Edge] = None):
        self.name = name
        self.nodes = nodes or []
        self.edges = edges or []
        self.created_at = datetime.utcnow()
    
    def add_node(self, node: Node):
        """Додавання вершини"""
        if not any(n.id == node.id for n in self.nodes):
            self.nodes.append(node)
    
    def add_edge(self, edge: Edge):
        """Додавання ребра"""
        # Перевірка існування вершин
        node_ids = {n.id for n in self.nodes}
        if edge.from_node in node_ids and edge.to_node in node_ids:
            self.edges.append(edge)
    
    def get_adjacency_matrix(self) -> Tuple[Dict, List[List[float]]]:
        """
        Створення матриці суміжності
        
        Returns:
            Tuple: (відображення id->індекс, матриця суміжності)
        """
        n = len(self.nodes)
        node_to_idx = {node.id: i for i, node in enumerate(self.nodes)}
        
        # Ініціалізація матриці нескінченностями
        matrix = [[float('inf')] * n for _ in range(n)]
        
        # Діагональ - нулі
        for i in range(n):
            matrix[i][i] = 0
        
        # Заповнення матриці вагами ребер
        for edge in self.edges:
            i = node_to_idx[edge.from_node]
            j = node_to_idx[edge.to_node]
            matrix[i][j] = edge.weight
            matrix[j][i] = edge.weight  # Граф неорієнтований
        
        return node_to_idx, matrix
    
    def to_dict(self) -> Dict:
        """Конвертація у словник для MongoDB"""
        return {
            'name': self.name,
            'nodes': [node.to_dict() for node in self.nodes],
            'edges': [edge.to_dict() for edge in self.edges],
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Graph':
        """Створення з словника"""
        graph = Graph(name=data['name'])
        graph.nodes = [Node.from_dict(n) for n in data['nodes']]
        graph.edges = [Edge.from_dict(e) for e in data['edges']]
        if 'created_at' in data:
            graph.created_at = data['created_at']
        return graph


class SearchResult:
    """Модель результату пошуку"""
    
    def __init__(self,
                 graph_id: str,
                 algorithm: str,
                 start: str,
                 end: str,
                 path: List[str],
                 distance: float,
                 execution_time: float,
                 iterations: int = None,
                 parameters: Dict = None):
        self.graph_id = graph_id
        self.algorithm = algorithm
        self.start = start
        self.end = end
        self.path = path
        self.distance = distance
        self.execution_time = execution_time
        self.iterations = iterations
        self.parameters = parameters or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Конвертація у словник для MongoDB"""
        result = {
            'graph_id': self.graph_id,
            'algorithm': self.algorithm,
            'start': self.start,
            'end': self.end,
            'path': self.path,
            'distance': self.distance,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp
        }
        
        if self.iterations is not None:
            result['iterations'] = self.iterations
        
        if self.parameters:
            result['parameters'] = self.parameters
        
        return result
    
    @staticmethod
    def from_dict(data: Dict) -> 'SearchResult':
        """Створення з словника"""
        return SearchResult(
            graph_id=data['graph_id'],
            algorithm=data['algorithm'],
            start=data['start'],
            end=data['end'],
            path=data['path'],
            distance=data['distance'],
            execution_time=data['execution_time'],
            iterations=data.get('iterations'),
            parameters=data.get('parameters', {})
        )