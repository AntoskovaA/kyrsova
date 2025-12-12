"""
Тести для роботи з базою даних MongoDB
"""
import unittest
from datetime import datetime
from database.mongo_client import MongoDB
from database.models import Graph, Node, Edge, SearchResult
from config import Config
import os


class TestMongoDBConnection(unittest.TestCase):
    """Тести підключення та ініціалізації MongoDB"""
    
    @classmethod
    def setUpClass(cls):
        """Налаштування тестової бази даних перед всіма тестами"""
        # Використання тестової бази даних
        cls.test_db_name = 'test_shortest_path_db'
        cls.db = MongoDB(
            uri=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'),
            database=cls.test_db_name
        )
    
    @classmethod
    def tearDownClass(cls):
        """Очищення та видалення тестової бази після всіх тестів"""
        # Видалення тестової бази
        cls.db.client.drop_database(cls.test_db_name)
        cls.db.close()
    
    def setUp(self):
        """Очищення колекцій перед кожним тестом"""
        self.db.db.graphs.delete_many({})
        self.db.db.search_results.delete_many({})
    
    def test_connection_successful(self):
        """Тест успішного підключення"""
        self.assertIsNotNone(self.db.client)
        self.assertIsNotNone(self.db.db)
    
    def test_database_name(self):
        """Тест перевірки назви бази даних"""
        self.assertEqual(self.db.db.name, self.test_db_name)


class TestGraphOperations(unittest.TestCase):
    """Тести CRUD-операцій з графами у MongoDB"""
    
    @classmethod
    def setUpClass(cls):
        cls.test_db_name = 'test_shortest_path_db'
        cls.db = MongoDB(
            uri=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'),
            database=cls.test_db_name
        )
    
    @classmethod
    def tearDownClass(cls):
        cls.db.client.drop_database(cls.test_db_name)
        cls.db.close()
    
    def setUp(self):
        self.db.db.graphs.delete_many({})
    
    def test_create_graph(self):
        """Тест створення графа"""
        graph = Graph(name="Test Graph")
        graph.add_node(Node('A', 'Node A', 0, 0))
        graph.add_node(Node('B', 'Node B', 100, 100))
        graph.add_edge(Edge('A', 'B', 10))
        
        graph_id = self.db.create_graph(graph.to_dict())
        
        self.assertIsNotNone(graph_id)
        self.assertTrue(len(graph_id) > 0)
    
    def test_get_graph(self):
        """Тест отримання графа за ID"""
        graph = Graph(name="Test Graph")
        graph.add_node(Node('A', 'Node A', 0, 0))
        graph.add_node(Node('B', 'Node B', 100, 100))
        
        graph_id = self.db.create_graph(graph.to_dict())
        retrieved_graph = self.db.get_graph(graph_id)
        
        self.assertIsNotNone(retrieved_graph)
        self.assertEqual(retrieved_graph['name'], "Test Graph")
        self.assertEqual(len(retrieved_graph['nodes']), 2)
        # Перевірка, що ID є рядком
        self.assertIsInstance(retrieved_graph['_id'], str)
    
    def test_get_all_graphs(self):
        """Тест отримання всіх графів з лімітом та сортуванням"""
        # Створення декількох графів
        for i in range(3):
            graph = Graph(name=f"Graph {i}")
            graph.add_node(Node('A', 'A', 0, 0))
            graph.add_node(Node('B', 'B', 100, 100))
            self.db.create_graph(graph.to_dict())
        
        graphs = self.db.get_all_graphs()
        
        self.assertEqual(len(graphs), 3)
    
    def test_update_graph(self):
        """Тест оновлення графа"""
        graph = Graph(name="Original Name")
        graph.add_node(Node('A', 'A', 0, 0))
        graph.add_node(Node('B', 'B', 100, 100))
        
        graph_id = self.db.create_graph(graph.to_dict())
        
        # Оновлення
        success = self.db.update_graph(graph_id, {'name': 'Updated Name'})
        
        self.assertTrue(success)
        
        # Перевірка
        updated_graph = self.db.get_graph(graph_id)
        self.assertEqual(updated_graph['name'], 'Updated Name')
    
    def test_delete_graph(self):
        """Тест видалення графа та пов'язаних результатів"""
        graph = Graph(name="To Delete")
        graph.add_node(Node('A', 'A', 0, 0))
        graph.add_node(Node('B', 'B', 100, 100))
        
        graph_id = self.db.create_graph(graph.to_dict())
        
        # Створення результату, пов'язаного з цим графом
        result = SearchResult(graph_id=graph_id, algorithm='ACO', start='A', end='B', path=['A', 'B'], distance=10, execution_time=0.1)
        self.db.save_search_result(result.to_dict())
        
        # Видалення
        success = self.db.delete_graph(graph_id)
        self.assertTrue(success)
        
        # Перевірка, що видалено
        deleted_graph = self.db.get_graph(graph_id)
        self.assertIsNone(deleted_graph)
        
        # Перевірка, що пов'язані результати також видалено
        remaining_results = self.db.get_graph_results(graph_id)
        self.assertEqual(len(remaining_results), 0)
    
    def test_get_nonexistent_graph(self):
        """Тест отримання неіснуючого графа"""
        fake_id = '507f1f77bcf86cd799439011'
        graph = self.db.get_graph(fake_id)
        
        self.assertIsNone(graph)


class TestSearchResultOperations(unittest.TestCase):
    """Тести операцій з результатами пошуку у MongoDB"""
    
    @classmethod
    def setUpClass(cls):
        cls.test_db_name = 'test_shortest_path_db'
        cls.db = MongoDB(
            uri=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'),
            database=cls.test_db_name
        )
    
    @classmethod
    def tearDownClass(cls):
        cls.db.client.drop_database(cls.test_db_name)
        cls.db.close()
    
    def setUp(self):
        self.db.db.graphs.delete_many({})
        self.db.db.search_results.delete_many({})
        
        # Створення тестового графа
        graph = Graph(name="Test Graph")
        graph.add_node(Node('A', 'A', 0, 0))
        graph.add_node(Node('B', 'B', 100, 100))
        self.graph_id = self.db.create_graph(graph.to_dict())
    
    def test_save_search_result(self):
        """Тест збереження результату пошуку"""
        result = SearchResult(
            graph_id=self.graph_id,
            algorithm='ACO',
            start='A',
            end='B',
            path=['A', 'B'],
            distance=10.5,
            execution_time=0.123,
            iterations=100,
            parameters={'num_ants': 50}
        )
        
        result_id = self.db.save_search_result(result.to_dict())
        
        self.assertIsNotNone(result_id)
    
    def test_get_search_result(self):
        """Тест отримання результату"""
        result = SearchResult(
            graph_id=self.graph_id,
            algorithm='Dijkstra',
            start='A',
            end='B',
            path=['A', 'B'],
            distance=10.5,
            execution_time=0.001
        )
        
        result_id = self.db.save_search_result(result.to_dict())
        retrieved_result = self.db.get_search_result(result_id)
        
        self.assertIsNotNone(retrieved_result)
        self.assertEqual(retrieved_result['algorithm'], 'Dijkstra')
        self.assertEqual(retrieved_result['distance'], 10.5)
        # Перевірка, що ID є рядками
        self.assertIsInstance(retrieved_result['_id'], str)
        self.assertIsInstance(retrieved_result['graph_id'], str)

    
    def test_get_graph_results(self):
        """Тест отримання всіх результатів для графа"""
        # Створення декількох результатів
        for i in range(3):
            result = SearchResult(
                graph_id=self.graph_id,
                algorithm='ACO',
                start='A',
                end='B',
                path=['A', 'B'],
                distance=10 + i,
                execution_time=0.1
            )
            self.db.save_search_result(result.to_dict())
        
        results = self.db.get_graph_results(self.graph_id)
        
        self.assertEqual(len(results), 3)
    
    def test_get_statistics(self):
        """Тест отримання статистики системи"""
        # Створення даних
        result = SearchResult(
            graph_id=self.graph_id,
            algorithm='ACO',
            start='A',
            end='B',
            path=['A', 'B'],
            distance=10,
            execution_time=0.1
        )
        self.db.save_search_result(result.to_dict())
        
        stats = self.db.get_statistics()
        
        self.assertIn('total_graphs', stats)
        self.assertIn('total_searches', stats)
        self.assertIn('algorithms_usage', stats)
        self.assertEqual(stats['total_graphs'], 1)
        self.assertEqual(stats['total_searches'], 1)


class TestModels(unittest.TestCase):
    """Тести моделей даних (Node, Edge, Graph, SearchResult)"""
    
    def test_node_creation(self):
        """Тест створення вершини"""
        node = Node('A', 'Node A', 100, 200)
        
        self.assertEqual(node.id, 'A')
    
    def test_graph_adjacency_matrix(self):
        """Тест створення матриці суміжності"""
        graph = Graph("Test")
        graph.add_node(Node('A', 'A', 0, 0))
        graph.add_node(Node('B', 'B', 100, 100))
        graph.add_edge(Edge('A', 'B', 10))
        
        node_to_idx, matrix = graph.get_adjacency_matrix()
        
        self.assertEqual(len(matrix), 2)
        self.assertEqual(matrix[0][1], 10)
        self.assertEqual(matrix[1][0], 10)  # Неорієнтований граф


if __name__ == '__main__':
    unittest.main()