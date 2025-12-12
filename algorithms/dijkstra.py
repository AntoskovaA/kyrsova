"""
Алгоритм Дейкстри для пошуку найкоротшого шляху
"""
import heapq
from typing import List, Dict, Tuple, Optional
import time


class Dijkstra:
    """
    Реалізація класичного алгоритму Дейкстри для пошуку найкоротшого шляху
    в графі з невід'ємними вагами.
    """
    
    def __init__(self, adjacency_matrix: List[List[float]], 
                 node_to_idx: Dict[str, int],
                 idx_to_node: Dict[int, str]):
        """
        Ініціалізація алгоритму.
        
        Args:
            adjacency_matrix: Матриця суміжності графа.
            node_to_idx: Відображення ID вершини -> індекс у матриці.
            idx_to_node: Відображення індекс -> ID вершини.
        """
        self.adjacency_matrix = adjacency_matrix
        self.node_to_idx = node_to_idx
        self.idx_to_node = idx_to_node
        self.num_nodes = len(adjacency_matrix)
    
    def find_shortest_path(self, start: str, end: str) -> Tuple[List[str], float, float]:
        """
        Пошук найкоротшого шляху між двома вершинами.
        
        Args:
            start: ID початкової вершини.
            end: ID кінцевої вершини.
            
        Returns:
            Tuple: (шлях у вигляді ID вершин, відстань, час виконання).
        """
        start_time = time.time()
        
        start_idx = self.node_to_idx[start]
        end_idx = self.node_to_idx[end]
        
        # Ініціалізація
        distances = [float('inf')] * self.num_nodes
        distances[start_idx] = 0
        previous = [None] * self.num_nodes
        
        # Пріоритетна черга: (відстань, вершина)
        pq = [(0, start_idx)]
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # Якщо досягли кінцевої вершини
            if current == end_idx:
                break
            
            # Перевірка сусідів
            for neighbor in range(self.num_nodes):
                if neighbor in visited:
                    continue
                
                edge_weight = self.adjacency_matrix[current][neighbor]
                
                if edge_weight != float('inf'):
                    new_distance = current_dist + edge_weight
                    
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current
                        heapq.heappush(pq, (new_distance, neighbor))
        
        # Відновлення шляху
        path = self._reconstruct_path(previous, start_idx, end_idx)
        distance = distances[end_idx]
        
        execution_time = time.time() - start_time
        
        return path, distance, execution_time
    
    def _reconstruct_path(self, previous: List[Optional[int]], 
                         start_idx: int, end_idx: int) -> List[str]:
        """
        Відновлення шляху з масиву попередників.
        
        Args:
            previous: Масив попередників.
            start_idx: Індекс початкової вершини.
            end_idx: Індекс кінцевої вершини.
            
        Returns:
            Список ID вершин шляху.
        """
        if previous[end_idx] is None and start_idx != end_idx:
            return []  # Шлях не знайдено
        
        path = []
        current = end_idx
        
        while current is not None:
            path.append(self.idx_to_node[current])
            current = previous[current]
        
        path.reverse()
        return path
    
    def find_all_shortest_paths(self, start: str) -> Dict[str, Tuple[List[str], float]]:
        """
        Пошук найкоротших шляхів до всіх вершин від заданої початкової вершини.
        
        Args:
            start: ID початкової вершини.
            
        Returns:
            Словник: {вершина: (шлях, відстань)}.
        """
        start_idx = self.node_to_idx[start]
        
        # Ініціалізація
        distances = [float('inf')] * self.num_nodes
        distances[start_idx] = 0
        previous = [None] * self.num_nodes
        
        # Пріоритетна черга
        pq = [(0, start_idx)]
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # Перевірка сусідів
            for neighbor in range(self.num_nodes):
                if neighbor in visited:
                    continue
                
                edge_weight = self.adjacency_matrix[current][neighbor]
                
                if edge_weight != float('inf'):
                    new_distance = current_dist + edge_weight
                    
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current
                        heapq.heappush(pq, (new_distance, neighbor))
        
        # Формування результатів
        results = {}
        for node_id, idx in self.node_to_idx.items():
            if idx != start_idx:
                path = self._reconstruct_path(previous, start_idx, idx)
                results[node_id] = (path, distances[idx])
        
        return results