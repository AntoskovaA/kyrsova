"""
Головні маршрути додатку
"""
from flask import Blueprint, render_template, jsonify
from database import MongoDB
from config import Config

main_bp = Blueprint('main', __name__)

# Глобальна змінна для БД (буде ініціалізована в app.py)
db = None


def init_db(database):
    """Ініціалізація БД для маршрутів"""
    global db
    db = database


@main_bp.route('/')
def index():
    """Головна сторінка"""
    return render_template('index.html')


@main_bp.route('/graph/editor')
def graph_editor():
    """Сторінка редактора графів"""
    return render_template('graph_editor.html')


@main_bp.route('/search')
def search_page():
    """Сторінка пошуку шляхів"""
    graphs = db.get_all_graphs(limit=100)
    return render_template('search.html', graphs=graphs)


@main_bp.route('/results/<result_id>')
def results_page(result_id):
    """Сторінка результатів"""
    result = db.get_search_result(result_id)
    if not result:
        return "Результат не знайдено", 404
    
    graph = db.get_graph(result['graph_id'])
    return render_template('results.html', result=result, graph=graph)


@main_bp.route('/api/statistics')
def get_statistics():
    """API для отримання статистики"""
    stats = db.get_statistics()
    return jsonify(stats)


@main_bp.route('/about')
def about():
    """Сторінка про проєкт"""
    return render_template('about.html')