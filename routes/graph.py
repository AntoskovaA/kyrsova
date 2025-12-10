"""
API маршрути для роботи з графами
"""
from flask import Blueprint, request, jsonify
from database import MongoDB
from database.models import Graph
from algorithms.graph_utils import GraphUtils
from config import Config
import logging

logger = logging.getLogger(__name__)

graph_bp = Blueprint('graph', __name__, url_prefix='/api/graph')

# Глобальна змінна для БД
db = None


def init_db(database):
    """Ініціалізація БД для маршрутів"""
    global db
    db = database


@graph_bp.route('/create', methods=['POST'])
def create_graph():
    """Створення нового графа"""
    try:
        data = request.get_json()
        
        # Валідація
        is_valid, message = GraphUtils.validate_graph(data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Перевірка обмежень
        if len(data['nodes']) > Config.MAX_GRAPH_NODES:
            return jsonify({'error': f'Максимум {Config.MAX_GRAPH_NODES} вершин'}), 400
        
        if len(data['edges']) > Config.MAX_GRAPH_EDGES:
            return jsonify({'error': f'Максимум {Config.MAX_GRAPH_EDGES} ребер'}), 400
        
        # Створення графа
        graph = Graph.from_dict(data)
        graph_id = db.create_graph(graph.to_dict())
        
        return jsonify({
            'success': True,
            'graph_id': graph_id,
            'message': 'Граф успішно створено'
        }), 201
        
    except Exception as e:
        logger.error(f"Помилка створення графа: {e}")
        return jsonify({'error': str(e)}), 500


@graph_bp.route('/<graph_id>', methods=['GET'])
def get_graph(graph_id):
    """Отримання графа за ID"""
    try:
        graph = db.get_graph(graph_id)
        if not graph:
            return jsonify({'error': 'Граф не знайдено'}), 404
        
        return jsonify(graph), 200
        
    except Exception as e:
        logger.error(f"Помилка отримання графа: {e}")
        return jsonify({'error': str(e)}), 500


@graph_bp.route('/all', methods=['GET'])
def get_all_graphs():
    """Отримання всіх графів"""
    try:
        limit = request.args.get('limit', 50, type=int)
        skip = request.args.get('skip', 0, type=int)
        
        graphs = db.get_all_graphs(limit=limit, skip=skip)
        
        return jsonify({
            'graphs': graphs,
            'count': len(graphs)
        }), 200
        
    except Exception as e:
        logger.error(f"Помилка отримання графів: {e}")
        return jsonify({'error': str(e)}), 500
    
    
@graph_bp.route('/<graph_id>', methods=['PUT'])
def update_graph(graph_id):
    """Оновлення графа"""
    try:
        data = request.get_json()
        
        # Валідація
        is_valid, message = GraphUtils.validate_graph(data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Оновлення
        success = db.update_graph(graph_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Граф оновлено'
            }), 200
        else:
            return jsonify({'error': 'Граф не знайдено'}), 404
            
    except Exception as e:
        logger.error(f"Помилка оновлення графа: {e}")
        return jsonify({'error': str(e)}), 500


@graph_bp.route('/<graph_id>', methods=['DELETE'])
def delete_graph(graph_id):
    """Видалення графа"""
    try:
        success = db.delete_graph(graph_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Граф видалено'
            }), 200
        else:
            return jsonify({'error': 'Граф не знайдено'}), 404
            
    except Exception as e:
        logger.error(f"Помилка видалення графа: {e}")
        return jsonify({'error': str(e)}), 500


@graph_bp.route('/generate/random', methods=['POST'])
def generate_random_graph():
    """Генерація випадкового графа"""
    try:
        data = request.get_json()
        num_nodes = data.get('num_nodes', 10)
        connectivity = data.get('connectivity', 0.3)
        
        # Обмеження
        num_nodes = min(num_nodes, Config.MAX_GRAPH_NODES)
        
        graph_data = GraphUtils.generate_random_graph(
            num_nodes=num_nodes,
            connectivity=connectivity
        )
        
        graph_id = db.create_graph(graph_data)
        
        return jsonify({
            'success': True,
            'graph_id': graph_id,
            'graph': graph_data
        }), 201
        
    except Exception as e:
        logger.error(f"Помилка генерації графа: {e}")
        return jsonify({'error': str(e)}), 500


@graph_bp.route('/generate/cities', methods=['POST'])
def generate_cities_graph():
    """Генерація графа міст України"""
    try:
        graph_data = GraphUtils.generate_cities_graph()
        graph_id = db.create_graph(graph_data)
        
        return jsonify({
            'success': True,
            'graph_id': graph_id,
            'graph': graph_data
        }), 201
        
    except Exception as e:
        logger.error(f"Помилка генерації графа міст: {e}")
        return jsonify({'error': str(e)}), 500