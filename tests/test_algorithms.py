"""
Юніт-тести для алгоритмів пошуку шляхів
"""
import unittest
import numpy as np
from algorithms.ant_colony import AntColonyOptimization
from algorithms.dijkstra import Dijkstra
from algorithms.graph_utils import GraphUtils


class TestGraphUtils(unittest.TestCase):
    """Тести для утиліт графа: генерації та валідації"""
    
    def test_generate_random_graph(self):
        """Тест генерації випадкового графа"""
        graph = GraphUtils.generate_random_graph(num_nodes=10, connectivity=0.3)
        
        self.assertIn('nodes', graph)
        self.assertIn('edges', graph)
        self.assertEqual(len(graph['nodes']), 10)
        self.assertTrue(len(graph['edges']) > 0)
    
    def test_generate_cities_graph(self):
        """Тест генерації графа міст"""
        graph = GraphUtils.generate_cities_graph()
        
        self.assertIn('nodes', graph)
        self.assertIn('edges', graph)
        self.assertEqual(len(graph['nodes']), 8)
        self.assertTrue(len(graph['edges']) > 0)
    
    def test_validate_graph_valid(self):
        """Тест валідації правильного графа"""
        graph = {
            'name': 'Test Graph',
            'nodes': [
                {'id': 'A', 'label': 'A', 'x': 0, 'y': 0},
                {'id': 'B', 'label': 'B', 'x': 100, 'y': 0}
            ],
            'edges': [
                {'from': 'A', 'to': 'B', 'weight': 10}
            ]
        }
        
        is_valid, message = GraphUtils.validate_graph(graph)
        self.assertTrue(is_valid)
    
    def test_validate_graph_invalid_nodes(self):
        """Тест валідації графа з недостатньою кількістю вершин"""
        graph = {
            'nodes': [
                {'id': 'A', 'label': 'A', 'x': 0, 'y': 0}
            ],
            'edges': []
        }
        
        is_valid, message = GraphUtils.validate_graph(graph)
        self.assertFalse(is_valid)
        self.assertIn('принаймні 2 вершини', message)
    
    def test_validate_graph_negative_weight(self):
        """Тест валідації графа з непозитивною вагою"""
        graph = {
            'nodes': [
                {'id': 'A', 'label': 'A', 'x': 0, 'y': 0},
                {'id': 'B', 'label': 'B', 'x': 100, 'y': 0}
            ],
            'edges': [
                {'from': 'A', 'to': 'B', 'weight': -5}
            ]
        }
        
        is_valid, message = GraphUtils.validate_graph(graph)
        self.assertFalse(is_valid)
        self.assertIn('додатною', message)
    
    def test_validate_graph_disconnected(self):
        """Тест валідації незв'язного графа"""
        graph = {
            'nodes': [
                {'id': 'A', 'label': 'A', 'x': 0, 'y': 0},
                {'id': 'B', 'label': 'B', 'x': 100, 'y': 0},
                {'id': 'C', 'label': 'C', 'x': 200, 'y': 0}
            ],
            'edges': [
                {'from': 'A', 'to': 'B', 'weight': 10}
                # C не з'єднана
            ]
        }
        
        is_valid, message = GraphUtils.validate_graph(graph)
        self.assertFalse(is_valid)
        self.assertIn('зв\'язним', message)
    
    def test_calculate_path_distance(self):
        """Тест обчислення довжини шляху"""
        adjacency_matrix = [
            [0, 10, float('inf')],
            [10, 0, 20],
            [float('inf'), 20, 0]
        ]
        node_to_idx = {'A': 0, 'B': 1, 'C': 2}
        path = ['A', 'B', 'C']
        
        distance = GraphUtils.calculate_path_distance(path, adjacency_matrix, node_to_idx)
        self.assertEqual(distance, 30)


class TestDijkstra(unittest.TestCase):
    """Тести для алгоритму Дейкстри"""
    
    def setUp(self):
        """Налаштування тестового графа перед кожним тестом"""
        # Граф: A --10-- B; A --5-- C; B --15-- D; C --20-- D
        self.adjacency_matrix = [
            [0, 10, 5, float('inf')],      # A
            [10, 0, float('inf'), 15],     # B
            [5, float('inf'), 0, 20],      # C
            [float('inf'), 15, 20, 0]      # D
        ]
        
        self.node_to_idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        self.idx_to_node = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        
        self.dijkstra = Dijkstra(
            self.adjacency_matrix,
            self.node_to_idx,
            self.idx_to_node
        )
    
    def test_shortest_path_direct(self):
        """Тест пошуку прямого шляху"""
        path, distance, _ = self.dijkstra.find_shortest_path('A', 'B')
        
        self.assertEqual(path, ['A', 'B'])
        self.assertEqual(distance, 10)
    
    def test_shortest_path_indirect(self):
        """Тест пошуку непрямого (оптимального) шляху"""
        path, distance, _ = self.dijkstra.find_shortest_path('A', 'D')
        
        # Оптимальний шлях: 25 (A->C->D або A->B->D)
        self.assertEqual(distance, 25)
        self.assertTrue(len(path) == 3)
    
    def test_same_start_end(self):
        """Тест коли початкова = кінцевій вершині"""
        path, distance, _ = self.dijkstra.find_shortest_path('A', 'A')
        
        self.assertEqual(path, ['A'])
        self.assertEqual(distance, 0)
    
    def test_execution_time(self):
        """Тест що час виконання вимірюється"""
        _, _, execution_time = self.dijkstra.find_shortest_path('A', 'D')
        
        self.assertGreaterEqual(execution_time, 0)
        self.assertIsInstance(execution_time, float)
    
    def test_find_all_shortest_paths(self):
        """Тест пошуку шляхів до всіх вершин"""
        results = self.dijkstra.find_all_shortest_paths('A')
        
        self.assertEqual(len(results), 3)  # До B, C, D
        self.assertEqual(results['B'][1], 10)
        self.assertEqual(results['C'][1], 5)
        self.assertEqual(results['D'][1], 25)


class TestAntColony(unittest.TestCase):
    """Тести для мурашиного алгоритму (ACO)"""
    
    def setUp(self):
        """Налаштування тестового графа перед кожним тестом"""
        self.adjacency_matrix = [
            [0, 10, 5, float('inf')],
            [10, 0, float('inf'), 15],
            [5, float('inf'), 0, 20],
            [float('inf'), 15, 20, 0]
        ]
        
        self.node_to_idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        self.idx_to_node = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
        
        self.aco = AntColonyOptimization(
            adjacency_matrix=self.adjacency_matrix,
            node_to_idx=self.node_to_idx,
            idx_to_node=self.idx_to_node,
            num_ants=10,
            iterations=50
        )
    
    def test_initialization(self):
        """Тест ініціалізації параметрів алгоритму"""
        self.assertEqual(self.aco.num_nodes, 4)
        self.assertEqual(self.aco.num_ants, 10)
        self.assertEqual(self.aco.iterations, 50)
        
        # Перевірка розміру матриць
        self.assertEqual(self.aco.pheromone.shape, (4, 4))
        self.assertEqual(self.aco.heuristic.shape, (4, 4))
    
    def test_find_path(self):
        """Тест пошуку шляху (має знайти нескінченний або близький до 25)"""
        path, distance, _, history = self.aco.find_shortest_path('A', 'D')
        
        self.assertIsInstance(path, list)
        self.assertTrue(len(path) == 3 or len(path) == 0)
        self.assertGreaterEqual(distance, 25)
    
    def test_convergence_history(self):
        """Тест збереження історії збіжності"""
        _, _, _, history = self.aco.find_shortest_path('A', 'D')
        
        self.assertIsInstance(history, list)
        self.assertTrue(len(history) > 0)
    
    def test_pheromone_update(self):
        """Тест оновлення феромонів"""
        initial_pheromone = self.aco.pheromone.copy()
        
        self.aco.find_shortest_path('A', 'D')
        
        # Феромони повинні змінитися
        self.assertFalse(np.array_equal(initial_pheromone, self.aco.pheromone))
    
    def test_unreachable_node(self):
        """Тест з недосяжною вершиною (шлях має бути не знайдено)"""
        # Граф з ізольованою вершиною
        disconnected_matrix = [
            [0, 10, float('inf'), float('inf')],
            [10, 0, float('inf'), float('inf')],
            [float('inf'), float('inf'), 0, 20],
            [float('inf'), float('inf'), 20, 0]
        ]
        
        aco = AntColonyOptimization(
            adjacency_matrix=disconnected_matrix,
            node_to_idx=self.node_to_idx,
            idx_to_node=self.idx_to_node,
            num_ants=5,
            iterations=20
        )
        
        path, distance, _, _ = aco.find_shortest_path('A', 'D')
        
        # Шлях не знайдено
        self.assertEqual(path, [])
        self.assertEqual(distance, float('inf'))


class TestAlgorithmComparison(unittest.TestCase):
    """Тести порівняння алгоритмів на ефективність"""
    
    def setUp(self):
        """Налаштування графа для порівняння"""
        self.adjacency_matrix = [
            [0, 2, 4, float('inf'), float('inf')],
            [2, 0, 1, 7, float('inf')],
            [4, 1, 0, 3, 5],
            [float('inf'), 7, 3, 0, 2],
            [float('inf'), float('inf'), 5, 2, 0]
        ]
        
        self.node_to_idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
        self.idx_to_node = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E'}
    
    def test_algorithms_find_optimal_distance(self):
        """Тест що Дейкстра знаходить оптимальну відстань, а ACO - близьку до неї"""
        dijkstra = Dijkstra(
            self.adjacency_matrix,
            self.node_to_idx,
            self.idx_to_node
        )
        
        aco = AntColonyOptimization(
            adjacency_matrix=self.adjacency_matrix,
            node_to_idx=self.node_to_idx,
            idx_to_node=self.idx_to_node,
            num_ants=100,
            iterations=200
        )
        
        dijk_path, dijk_dist, _ = dijkstra.find_shortest_path('A', 'E')
        aco_path, aco_dist, _, _ = aco.find_shortest_path('A', 'E')
        
        # Оптимальний шлях: A->B->C->D->E (2+1+3+2 = 8)
        self.assertEqual(dijk_dist, 8.0)
        
        # ACO має бути близьким до оптимуму (в межах 20% для великих ітерацій)
        self.assertLessEqual(aco_dist, dijk_dist * 1.20)
    
    def test_dijkstra_faster_than_aco_on_small_graph(self):
        """Тест що Дейкстра швидша за ACO на невеликому графі"""
        dijkstra = Dijkstra(
            self.adjacency_matrix,
            self.node_to_idx,
            self.idx_to_node
        )
        
        aco = AntColonyOptimization(
            adjacency_matrix=self.adjacency_matrix,
            node_to_idx=self.node_to_idx,
            idx_to_node=self.idx_to_node,
            num_ants=50,
            iterations=100
        )
        
        _, _, dijk_time = dijkstra.find_shortest_path('A', 'E')
        _, _, aco_time, _ = aco.find_shortest_path('A', 'E')
        
        # Дейкстра має бути швидшою
        self.assertLess(dijk_time, aco_time)


if __name__ == '__main__':
    unittest.main()