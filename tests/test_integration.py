"""
Інтеграційні тести для всієї системи: перевірка API та взаємодії компонентів
"""
import unittest
import json
from app import create_app
from database.mongo_client import MongoDB 
from database.models import Graph, Node, Edge
import os

# Визначаємо тестову назву БД
TEST_DB_NAME = 'test_integration_db'

class TestFlaskAPI(unittest.TestCase):
    """Інтеграційні тести Flask API"""
    
    @classmethod
    def setUpClass(cls):
        """Налаштування перед всіма тестами: ініціалізація Flask та MongoDB"""
        # Створення додатку в тестовому режимі
        cls.app = create_app('default')
        cls.app.config['TESTING'] = True
        # Перевизначаємо назву БД на тестову
        cls.app.config['MONGODB_DATABASE'] = TEST_DB_NAME
        cls.client = cls.app.test_client()
        
        # Ініціалізація MongoDB для очищення
        cls.db = MongoDB(
            uri=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'),
            database=TEST_DB_NAME
        )
    
    @classmethod
    def tearDownClass(cls):
        """Очищення та видалення тестової бази після всіх тестів"""
        # Видалення тестової бази даних
        cls.db.client.drop_database(TEST_DB_NAME)
        cls.db.close()
    
    def setUp(self):
        """Очищення колекцій перед кожним тестом"""
        self.db.db.graphs.delete_many({})
        self.db.db.search_results.delete_many({})
        
        # Базовий граф для тестів
        self.base_graph_data = {
            'name': 'Test Graph for Search',
            'nodes': [
                {'id': 'A', 'label': 'A', 'x': 0, 'y': 0},
                {'id': 'B', 'label': 'B', 'x': 100, 'y': 0},
                {'id': 'C', 'label': 'C', 'x': 200, 'y': 0}
            ],
            'edges': [
                {'from': 'A', 'to': 'B', 'weight': 10},
                {'from': 'B', 'to': 'C', 'weight': 5},
                {'from': 'A', 'to': 'C', 'weight': 30}
            ]
        }
    
    # --- ТЕСТИ ГРАФІВ ---
    
    def test_a_graph_creation_and_retrieval(self):
        """Тест створення та отримання графа через API"""
        # 1. Створення графа
        response = self.client.post(
            '/api/graph/create',
            data=json.dumps(self.base_graph_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('graph_id', data)
        
        self.test_graph_id = data['graph_id']
        
        # 2. Отримання графа
        response = self.client.get(f'/api/graph/{self.test_graph_id}')
        self.assertEqual(response.status_code, 200)
        retrieved_graph = response.get_json()
        self.assertEqual(retrieved_graph['name'], 'Test Graph for Search')
        self.assertEqual(len(retrieved_graph['nodes']), 3)

    def test_b_random_graph_generation(self):
        """Тест генерації випадкового графа через API"""
        num_nodes = 5
        response = self.client.post(
            '/api/graph/generate/random',
            data=json.dumps({'num_nodes': num_nodes, 'connectivity': 0.5}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['graph']['nodes']), num_nodes)

    # --- ТЕСТИ ПОШУКУ (Повний цикл) ---

    def test_c_shortest_path_dijkstra_full_cycle(self):
        """Тест повного циклу: Створення -> Пошук (Dijkstra)"""
        
        # 1. Створення графа
        response = self.client.post(
            '/api/graph/create',
            data=json.dumps(self.base_graph_data),
            content_type='application/json'
        )
        graph_id = response.get_json()['graph_id']

        # 2. Виконання пошуку (ЗАПИС В БД через API)
        search_payload = {
            'graph_id': graph_id,
            'algorithm': 'Dijkstra',
            'start': 'A',
            'end': 'C'
        }
        response = self.client.post(
            '/api/search/run',
            data=json.dumps(search_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        
        # Перевірка API відповіді
        self.assertEqual(result['distance'], 15.0)
        
        # 3. Підготовка до читання
        result_id_str = result['result_id']

        read_response = self.client.get(f'/api/search/result/{result_id_str}')
        
        # Перевіряємо, що API успішно повернув результат (Код 200)
        self.assertEqual(read_response.status_code, 200, 
                         f"API не зміг прочитати результат з ID {result_id_str} після запису.")
        
        db_result = read_response.get_json()
        
        # Фінальна перевірка, що дані коректні
        self.assertEqual(db_result['algorithm'], 'Dijkstra')
        self.assertEqual(db_result['distance'], 15.0)

    def test_d_compare_algorithms(self):
        """Тест порівняння ACO та Дейкстри"""
        # 1. Створення графа
        response = self.client.post(
            '/api/graph/create',
            data=json.dumps(self.base_graph_data),
            content_type='application/json'
        )
        graph_id = response.get_json()['graph_id']

        # 2. Виконання порівняння
        compare_payload = {
            'graph_id': graph_id,
            'start': 'A',
            'end': 'C',
            'aco_parameters': {'iterations': 50, 'num_ants': 20}
        }
        response = self.client.post(
            '/api/search/compare',
            data=json.dumps(compare_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        # 3. Перевірка порівняння
        self.assertIn('aco', data)
        self.assertIn('dijkstra', data)
        self.assertEqual(data['dijkstra']['distance'], 15.0)
        self.assertTrue(data['aco']['distance'] >= 15.0)

    # --- ТЕСТИ СТАТИСТИКИ ---
    
    def test_e_get_statistics(self):
        """Тест отримання загальної статистики"""
        # Припускаючи, що попередні тести успішно зберегли дані
        response = self.client.get('/api/statistics')
        self.assertEqual(response.status_code, 200)
        stats = response.get_json()
        
        # Очікується, що було збережено щонайменше 1 граф та результати
        self.assertTrue(stats['total_graphs'] >= 1)
        self.assertTrue(stats['total_searches'] >= 1)