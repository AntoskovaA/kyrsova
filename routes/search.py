"""
API маршрути для пошуку шляхів
"""
from flask import Blueprint, request, jsonify
from database import MongoDB
from database.models import Graph, SearchResult
from algorithms.ant_colony import AntColonyOptimization
from algorithms.dijkstra import Dijkstra
from config import Config
import logging

logger = logging.getLogger(__name__)

search_bp = Blueprint('search', __name__, url_prefix='/api/search')

# Глобальна змінна для БД
db = None


def init_db(database):
    """Ініціалізація БД для маршрутів"""
    global db
    db = database


@search_bp.route('/run', methods=['POST'])
def run_search():
    """
    Виконання пошуку шляху
    
    Очікувані параметри:
    {
        "graph_id": "...",
        "algorithm": "ACO" або "Dijkstra",
        "start": "node_id",
        "end": "node_id",
        "parameters": {
            "num_ants": 50,
            "alpha": 1.0,
            "beta": 5.0,
            "evaporation": 0.5,
            "iterations": 100
        }
    }
    """
    try:
        data = request.get_json()
        
        # Валідація вхідних даних
        required_fields = ['graph_id', 'algorithm', 'start', 'end']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Поле "{field}" обов\'язкове'}), 400
        
        graph_id = data['graph_id']
        algorithm = data['algorithm']
        start = data['start']
        end = data['end']
        parameters = data.get('parameters', {})
        
        # Отримання графа
        graph_data = db.get_graph(graph_id)
        if not graph_data:
            return jsonify({'error': 'Граф не знайдено'}), 404
        
        # Створення об'єкта графа
        graph = Graph.from_dict(graph_data)
        
        # Перевірка існування вершин
        node_ids = {node.id for node in graph.nodes}
        if start not in node_ids:
            return jsonify({'error': f'Вершина "{start}" не існує'}), 400
        if end not in node_ids:
            return jsonify({'error': f'Вершина "{end}" не існує'}), 400
        
        # Отримання матриці суміжності
        node_to_idx, adjacency_matrix = graph.get_adjacency_matrix()
        idx_to_node = {v: k for k, v in node_to_idx.items()}
        
        # Виконання пошуку згідно з вибраним алгоритмом
        if algorithm == 'ACO':
            result = _run_aco(
                adjacency_matrix, 
                node_to_idx, 
                idx_to_node,
                start, 
                end, 
                parameters
            )
        elif algorithm == 'Dijkstra':
            result = _run_dijkstra(
                adjacency_matrix,
                node_to_idx,
                idx_to_node,
                start,
                end
            )
        else:
            return jsonify({'error': f'Невідомий алгоритм: {algorithm}'}), 400
        
        # Збереження результату
        search_result = SearchResult(
            graph_id=graph_id,
            algorithm=algorithm,
            start=start,
            end=end,
            path=result['path'],
            distance=result['distance'],
            execution_time=result['execution_time'],
            iterations=result.get('iterations'),
            parameters=parameters
        )
        
        result_id = db.save_search_result(search_result.to_dict())
        
        # Додавання ID результату до відповіді
        result['result_id'] = result_id
        result['graph_id'] = graph_id
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Помилка пошуку: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def _run_aco(adjacency_matrix, node_to_idx, idx_to_node, start, end, parameters):
    """Виконання мурашиного алгоритму"""
    # Параметри з Config якщо не вказано
    num_ants = parameters.get('num_ants', Config.DEFAULT_ACO_PARAMS['num_ants'])
    alpha = parameters.get('alpha', Config.DEFAULT_ACO_PARAMS['alpha'])
    beta = parameters.get('beta', Config.DEFAULT_ACO_PARAMS['beta'])
    evaporation = parameters.get('evaporation', Config.DEFAULT_ACO_PARAMS['evaporation'])
    iterations = parameters.get('iterations', Config.DEFAULT_ACO_PARAMS['iterations'])
    
    # Створення алгоритму
    aco = AntColonyOptimization(
        adjacency_matrix=adjacency_matrix,
        node_to_idx=node_to_idx,
        idx_to_node=idx_to_node,
        num_ants=num_ants,
        alpha=alpha,
        beta=beta,
        evaporation=evaporation,
        iterations=iterations
    )
    
    # Виконання пошуку
    path, distance, execution_time, history = aco.find_shortest_path(start, end)
    
    return {
        'algorithm': 'ACO',
        'path': path,
        'distance': distance if distance != float('inf') else None,
        'execution_time': execution_time,
        'iterations': iterations,
        'history': history,
        'parameters': {
            'num_ants': num_ants,
            'alpha': alpha,
            'beta': beta,
            'evaporation': evaporation,
            'iterations': iterations
        }
    }


def _run_dijkstra(adjacency_matrix, node_to_idx, idx_to_node, start, end):
    """Виконання алгоритму Дейкстри"""
    dijkstra = Dijkstra(
        adjacency_matrix=adjacency_matrix,
        node_to_idx=node_to_idx,
        idx_to_node=idx_to_node
    )
    
    path, distance, execution_time = dijkstra.find_shortest_path(start, end)
    
    return {
        'algorithm': 'Dijkstra',
        'path': path,
        'distance': distance if distance != float('inf') else None,
        'execution_time': execution_time
    }


@search_bp.route('/compare', methods=['POST'])
def compare_algorithms():
    """
    Порівняння алгоритмів
    
    Очікувані параметри:
    {
        "graph_id": "...",
        "start": "node_id",
        "end": "node_id",
        "aco_parameters": {...}
    }
    """
    try:
        data = request.get_json()
        
        graph_id = data['graph_id']
        start = data['start']
        end = data['end']
        aco_parameters = data.get('aco_parameters', {})
        
        # Отримання графа
        graph_data = db.get_graph(graph_id)
        if not graph_data:
            return jsonify({'error': 'Граф не знайдено'}), 404
        
        graph = Graph.from_dict(graph_data)
        node_to_idx, adjacency_matrix = graph.get_adjacency_matrix()
        idx_to_node = {v: k for k, v in node_to_idx.items()}
        
        # Виконання обох алгоритмів
        aco_result = _run_aco(
            adjacency_matrix,
            node_to_idx,
            idx_to_node,
            start,
            end,
            aco_parameters
        )
        
        dijkstra_result = _run_dijkstra(
            adjacency_matrix,
            node_to_idx,
            idx_to_node,
            start,
            end
        )
        
        # Збереження обох результатів
        for result in [aco_result, dijkstra_result]:
            search_result = SearchResult(
                graph_id=graph_id,
                algorithm=result['algorithm'],
                start=start,
                end=end,
                path=result['path'],
                distance=result['distance'],
                execution_time=result['execution_time'],
                iterations=result.get('iterations'),
                parameters=result.get('parameters', {})
            )
            db.save_search_result(search_result.to_dict())
        
        return jsonify({
            'aco': aco_result,
            'dijkstra': dijkstra_result,
            'comparison': {
                'distance_difference': abs(aco_result['distance'] - dijkstra_result['distance']) if aco_result['distance'] and dijkstra_result['distance'] else None,
                'time_difference': aco_result['execution_time'] - dijkstra_result['execution_time'],
                'same_path': aco_result['path'] == dijkstra_result['path']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Помилка порівняння: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@search_bp.route('/history/<graph_id>', methods=['GET'])
def get_search_history(graph_id):
    """Отримання історії пошуків для графа"""
    try:
        limit = request.args.get('limit', 20, type=int)
        results = db.get_graph_results(graph_id, limit=limit)
        
        return jsonify({
            'graph_id': graph_id,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Помилка отримання історії: {e}")
        return jsonify({'error': str(e)}), 500


@search_bp.route('/result/<result_id>', methods=['GET'])
def get_result(result_id):
    """Отримання конкретного результату пошуку"""
    try:
        result = db.get_search_result(result_id)
        
        if not result:
            return jsonify({'error': 'Результат не знайдено'}), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Помилка отримання результату: {e}")
        return jsonify({'error': str(e)}), 500