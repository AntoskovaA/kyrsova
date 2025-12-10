"""
Мурашиний алгоритм (Ant Colony Optimization) для пошуку найкоротшого шляху
"""
import numpy as np
from typing import List, Dict, Tuple
import time
import random


class AntColonyOptimization:
    """Реалізація мурашиного алгоритму оптимізації"""
    
    def __init__(self,
                 adjacency_matrix: List[List[float]],
                 node_to_idx: Dict[str, int],
                 idx_to_node: Dict[int, str],
                 num_ants: int = 50,
                 alpha: float = 1.0,
                 beta: float = 5.0,
                 evaporation: float = 0.5,
                 iterations: int = 100,
                 q: float = 100.0):
        """
        Ініціалізація алгоритму
        
        Args:
            adjacency_matrix: Матриця суміжності
            node_to_idx: Відображення ID вершини -> індекс
            idx_to_node: Відображення індекс -> ID вершини
            num_ants: Кількість мурах
            alpha: Вплив феромону (0-10)
            beta: Вплив евристики/відстані (0-10)
            evaporation: Коефіцієнт випаровування феромону (0-1)
            iterations: Кількість ітерацій
            q: Константа для оновлення феромону
        """
        self.adjacency_matrix = np.array(adjacency_matrix)
        self.node_to_idx = node_to_idx
        self.idx_to_node = idx_to_node
        self.num_nodes = len(adjacency_matrix)
        
        # Параметри алгоритму
        self.num_ants = num_ants
        self.alpha = alpha  # Вага феромону
        self.beta = beta    # Вага евристики
        self.evaporation = evaporation
        self.iterations = iterations
        self.q = q
        
        # Ініціалізація матриці феромонів
        self.pheromone = np.ones((self.num_nodes, self.num_nodes))
        
        # Евристична інформація (1/відстань)
        self.heuristic = np.zeros((self.num_nodes, self.num_nodes))
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                if self.adjacency_matrix[i][j] != float('inf') and i != j:
                    self.heuristic[i][j] = 1.0 / self.adjacency_matrix[i][j]
        
        # Історія для візуалізації
        self.history = []
    
    def find_shortest_path(self, start: str, end: str) -> Tuple[List[str], float, float, List[Dict]]:
        """
        Пошук найкоротшого шляху
        
        Args:
            start: ID початкової вершини
            end: ID кінцевої вершини
            
        Returns:
            Tuple: (шлях, відстань, час виконання, історія)
        """
        start_time = time.time()
        
        start_idx = self.node_to_idx[start]
        end_idx = self.node_to_idx[end]
        
        best_path = None
        best_distance = float('inf')
        self.history = []
        
        # Головний цикл ітерацій
        for iteration in range(self.iterations):
            # Всі мурахи шукають шлях
            all_paths = []
            all_distances = []
            
            for ant in range(self.num_ants):
                path, distance = self._construct_solution(start_idx, end_idx)
                
                if path and distance < best_distance:
                    best_path = path
                    best_distance = distance
                
                all_paths.append(path)
                all_distances.append(distance)
            
            # Оновлення феромонів
            self._update_pheromones(all_paths, all_distances)
            
            # Збереження історії для візуалізації
            if iteration % 10 == 0 or iteration == self.iterations - 1:
                self.history.append({
                    'iteration': iteration,
                    'best_distance': best_distance,
                    'best_path': [self.idx_to_node[idx] for idx in best_path] if best_path else [],
                    'avg_distance': np.mean([d for d in all_distances if d != float('inf')])
                })
        
        execution_time = time.time() - start_time
        
        # Конвертація індексів у ID вершин
        if best_path:
            path_ids = [self.idx_to_node[idx] for idx in best_path]
        else:
            path_ids = []
        
        return path_ids, best_distance, execution_time, self.history
    
    def _construct_solution(self, start_idx: int, end_idx: int) -> Tuple[List[int], float]:
        """
        Побудова рішення однією мурахою
        
        Args:
            start_idx: Індекс початкової вершини
            end_idx: Індекс кінцевої вершини
            
        Returns:
            Tuple: (шлях у вигляді індексів, загальна відстань)
        """
        path = [start_idx]
        visited = {start_idx}
        current = start_idx
        total_distance = 0.0
        
        # Побудова шляху до кінцевої вершини
        while current != end_idx and len(visited) < self.num_nodes:
            next_node = self._select_next_node(current, visited, end_idx)
            
            if next_node is None:
                # Тупик - шлях не знайдено
                return [], float('inf')
            
            # Додавання до шляху
            edge_distance = self.adjacency_matrix[current][next_node]
            total_distance += edge_distance
            path.append(next_node)
            visited.add(next_node)
            current = next_node
        
        # Перевірка чи досягли кінцевої вершини
        if current != end_idx:
            return [], float('inf')
        
        return path, total_distance
    
    def _select_next_node(self, current: int, visited: set, end_idx: int) -> int:
        """
        Вибір наступної вершини на основі ймовірностей
        
        Args:
            current: Поточна вершина
            visited: Відвідані вершини
            end_idx: Індекс кінцевої вершини
            
        Returns:
            Індекс наступної вершини або None
        """
        # Доступні вершини
        unvisited = [i for i in range(self.num_nodes) 
                    if i not in visited and self.adjacency_matrix[current][i] != float('inf')]
        
        if not unvisited:
            return None
        
        # Обчислення ймовірностей
        probabilities = []
        
        for node in unvisited:
            pheromone = self.pheromone[current][node] ** self.alpha
            heuristic = self.heuristic[current][node] ** self.beta
            
            # Бонус якщо це кінцева вершина
            if node == end_idx:
                heuristic *= 2.0
            
            probabilities.append(pheromone * heuristic)
        
        # Нормалізація ймовірностей
        total = sum(probabilities)
        if total == 0:
            probabilities = [1.0] * len(unvisited)
            total = len(unvisited)
        
        probabilities = [p / total for p in probabilities]
        
        # Вибір вершини згідно з ймовірностями
        return np.random.choice(unvisited, p=probabilities)
    
    def _update_pheromones(self, all_paths: List[List[int]], all_distances: List[float]):
        """
        Оновлення феромонів після ітерації
        
        Args:
            all_paths: Список шляхів всіх мурах
            all_distances: Список відстаней всіх мурах
        """
        # Випаровування феромонів
        self.pheromone *= (1 - self.evaporation)
        
        # Додавання нових феромонів
        for path, distance in zip(all_paths, all_distances):
            if not path or distance == float('inf'):
                continue
            
            # Кількість феромону обернено пропорційна довжині шляху
            pheromone_deposit = self.q / distance
            
            # Оновлення ребер шляху
            for i in range(len(path) - 1):
                from_node = path[i]
                to_node = path[i + 1]
                self.pheromone[from_node][to_node] += pheromone_deposit
                self.pheromone[to_node][from_node] += pheromone_deposit
        
        # Обмеження значень феромонів
        self.pheromone = np.clip(self.pheromone, 0.1, 10.0)
    
    def get_pheromone_matrix(self) -> List[List[float]]:
        """
        Отримання поточної матриці феромонів
        
        Returns:
            Матриця феромонів
        """
        return self.pheromone.tolist()