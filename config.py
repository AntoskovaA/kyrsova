"""
Конфігурація додатку
"""
import os
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()


class Config:
    """Базова конфігурація для всього додатку"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'shortest_path_db')
    
    # Параметри алгоритмів за замовчуванням
    DEFAULT_ACO_PARAMS = {
        'num_ants': int(os.getenv('DEFAULT_NUM_ANTS', 50)),
        'alpha': float(os.getenv('DEFAULT_ALPHA', 1.0)),
        'beta': float(os.getenv('DEFAULT_BETA', 5.0)),
        'evaporation': float(os.getenv('DEFAULT_EVAPORATION', 0.5)),
        'iterations': int(os.getenv('DEFAULT_ITERATIONS', 100))
    }
    
    # Обмеження
    MAX_GRAPH_NODES = int(os.getenv('MAX_GRAPH_NODES', 100))
    MAX_GRAPH_EDGES = int(os.getenv('MAX_GRAPH_EDGES', 500))
    
    # Колекції MongoDB
    GRAPHS_COLLECTION = 'graphs'
    RESULTS_COLLECTION = 'search_results'


class DevelopmentConfig(Config):
    """Конфігурація для режиму розробки"""
    DEBUG = True


class ProductionConfig(Config):
    """Конфігурація для режиму production"""
    DEBUG = False


# Вибір конфігурації
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}