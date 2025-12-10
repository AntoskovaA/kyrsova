"""
Утиліти для роботи з графами
"""
import random
from typing import List, Dict, Tuple
import math


class GraphUtils:
    """Допоміжні функції для роботи з графами"""
    
    @staticmethod
    def generate_random_graph(num_nodes: int, 
                            connectivity: float = 0.3,
                            min_weight: float = 1.0,
                            max_weight: float = 100.0) -> Dict:
        """
        Генерація випадкового графа
        
        Args:
            num_nodes: Кількість вершин
            connectivity: Щільність з'єднань (0-1)
            min_weight: Мінімальна вага ребра
            max_weight: Максимальна вага ребра
            
        Returns:
            Словник з даними графа
        """
        nodes = []
        edges = []
        
        # Генерація вершин по колу
        center_x, center_y = 400, 300
        radius = 200
        
        for i in range(num_nodes):
            angle = 2 * math.pi * i / num_nodes
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            nodes.append({
                'id': f'node_{i}',
                'label': f'V{i}',
                'x': x,
                'y': y
            })
        
        # Генерація ребер
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if random.random() < connectivity:
                    weight = round(random.uniform(min_weight, max_weight), 2)
                    edges.append({
                        'from': f'node_{i}',
                        'to': f'node_{j}',
                        'weight': weight
                    })
        
        # Забезпечення зв'язності графа (мінімальне остовне дерево)
        if len(edges) < num_nodes - 1:
            for i in range(num_nodes - 1):
                if not any(e['from'] == f'node_{i}' or e['to'] == f'node_{i}' for e in edges):
                    weight = round(random.uniform(min_weight, max_weight), 2)
                    edges.append({
                        'from': f'node_{i}',
                        'to': f'node_{i+1}',
                        'weight': weight
                    })
        
        return {
            'name': f'Random Graph ({num_nodes} nodes)',
            'nodes': nodes,
            'edges': edges
        }
    
    @staticmethod
    def generate_cities_graph() -> Dict:
        """
        Генерація графа міст України (приклад)
        
        Returns:
            Словник з даними графа міст
        """
        nodes = [
            {'id': 'kyiv', 'label': 'Київ', 'x': 500, 'y': 200},
            {'id': 'lviv', 'label': 'Львів', 'x': 100, 'y': 250},
            {'id': 'odesa', 'label': 'Одеса', 'x': 400, 'y': 500},
            {'id': 'kharkiv', 'label': 'Харків', 'x': 700, 'y': 200},
            {'id': 'dnipro', 'label': 'Дніпро', 'x': 650, 'y': 350},
            {'id': 'rivne', 'label': 'Рівне', 'x': 250, 'y': 150},
            {'id': 'zhytomyr', 'label': 'Житомир', 'x': 350, 'y': 150},
            {'id': 'vinnytsia', 'label': 'Вінниця', 'x': 350, 'y': 300},
        ]
        
        # Реальні відстані між містами (приблизно в км)
        edges = [
            {'from': 'kyiv', 'to': 'lviv', 'weight': 540},
            {'from': 'kyiv', 'to': 'odesa', 'weight': 475},
            {'from': 'kyiv', 'to': 'kharkiv', 'weight': 480},
            {'from': 'kyiv', 'to': 'dnipro', 'weight': 480},
            {'from': 'kyiv', 'to': 'rivne', 'weight': 310},
            {'from': 'kyiv', 'to': 'zhytomyr', 'weight': 140},
            {'from': 'kyiv', 'to': 'vinnytsia', 'weight': 270},
            {'from': 'lviv', 'to': 'rivne', 'weight': 210},
            {'from': 'lviv', 'to': 'vinnytsia', 'weight': 380},
            {'from': 'odesa', 'to': 'vinnytsia', 'weight': 340},
            {'from': 'kharkiv', 'to': 'dnipro', 'weight': 220},
            {'from': 'rivne', 'to': 'zhytomyr', 'weight': 180},
            {'from': 'zhytomyr', 'to': 'vinnytsia', 'weight': 130},
        ]
        
        return {
            'name': 'Міста України',
            'nodes': nodes,
            'edges': edges
        }
    
    @staticmethod
    def validate_graph(graph_data: Dict) -> Tuple[bool, str]:
        """
        Валідація графа
        
        Args:
            graph_data: Дані графа
            
        Returns:
            Tuple: (валідність, повідомлення про помилку)
        """
        # Перевірка наявності полів
        if 'nodes' not in graph_data or 'edges' not in graph_data:
            return False, "Граф повинен містити 'nodes' та 'edges'"
        
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        
        # Перевірка кількості вершин
        if len(nodes) < 2:
            return False, "Граф повинен містити принаймні 2 вершини"
        
        # Перевірка унікальності ID вершин
        node_ids = [n['id'] for n in nodes]
        if len(node_ids) != len(set(node_ids)):
            return False, "ID вершин повинні бути унікальними"
        
        # Перевірка ребер
        node_ids_set = set(node_ids)
        for edge in edges:
            if edge['from'] not in node_ids_set:
                return False, f"Вершина '{edge['from']}' не існує"
            if edge['to'] not in node_ids_set:
                return False, f"Вершина '{edge['to']}' не існує"
            if edge['weight'] <= 0:
                return False, f"Вага ребра повинна бути додатною"
        
        # Перевірка зв'язності графа
        if not GraphUtils._is_connected(nodes, edges):
            return False, "Граф повинен бути зв'язним"
        
        return True, "Граф валідний"
    
    @staticmethod
    def _is_connected(nodes: List[Dict], edges: List[Dict]) -> bool:
        """
        Перевірка зв'язності графа (DFS)
        
        Args:
            nodes: Список вершин
            edges: Список ребер
            
        Returns:
            True якщо граф зв'язний
        """
        if not nodes:
            return False
        
        # Побудова списку суміжності
        adjacency = {node['id']: [] for node in nodes}
        for edge in edges:
            adjacency[edge['from']].append(edge['to'])
            adjacency[edge['to']].append(edge['from'])
        
        # DFS
        visited = set()
        stack = [nodes[0]['id']]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            stack.extend(adjacency[current])
        
        return len(visited) == len(nodes)
    
    @staticmethod
    def calculate_path_distance(path: List[str], 
                                adjacency_matrix: List[List[float]],
                                node_to_idx: Dict[str, int]) -> float:
        """
        Обчислення довжини шляху
        
        Args:
            path: Список ID вершин
            adjacency_matrix: Матриця суміжності
            node_to_idx: Відображення ID -> індекс
            
        Returns:
            Загальна довжина шляху
        """
        if len(path) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(path) - 1):
            from_idx = node_to_idx[path[i]]
            to_idx = node_to_idx[path[i + 1]]
            distance = adjacency_matrix[from_idx][to_idx]
            
            if distance == float('inf'):
                return float('inf')
            
            total_distance += distance
        
        return total_distance