"""
Головний файл Flask додатку
Система пошуку найкоротших шляхів з використанням ройових алгоритмів
"""
from flask import Flask, render_template
from flask_cors import CORS
from database import MongoDB
from routes import main_bp, graph_bp, search_bp
from routes.main import init_db as main_init_db
from routes.graph import init_db as graph_init_db
from routes.search import init_db as search_init_db
from config import config
import logging
import os

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """
    Фабрика додатку Flask. Ініціалізує конфігурацію, базу даних та маршрути.
    
    Args:
        config_name: Назва конфігурації ('development', 'production').
        
    Returns:
        Flask додаток.
    """
    app = Flask(__name__)
    
    # Завантаження конфігурації
    app.config.from_object(config[config_name])
    
    # CORS для API
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Ініціалізація MongoDB
    try:
        db = MongoDB(
            uri=app.config['MONGODB_URI'],
            database=app.config['MONGODB_DATABASE']
        )
        logger.info("База даних ініціалізована")
        
        # Передача об'єкта БД у Blueprints маршрутів
        main_init_db(db)
        graph_init_db(db)
        search_init_db(db)
        
    except Exception as e:
        logger.error(f" Помилка ініціалізації БД: {e}")
        raise
    
    # Реєстрація blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(graph_bp)
    app.register_blueprint(search_bp)
    
    # Обробник помилок 404
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404
    
    # Обробник помилок 500
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal error: {e}")
        return render_template('500.html'), 500
    
    # Контекстний процесор для шаблонів
    @app.context_processor
    def inject_config():
        """Вставляє глобальні змінні у всі шаблони Jinja2"""
        return {
            'app_name': 'Shortest Path Finder',
            'version': '1.0.0'
        }
    
    logger.info("Flask додаток створено")
    return app


# Створення додатку
app = create_app(os.getenv('FLASK_ENV', 'development'))


if __name__ == '__main__':
    # Параметри запуску
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Запуск сервера на http://{host}:{port}")
    logger.info(f"Режим: {'Development' if debug else 'Production'}")
    
    app.run(host=host, port=port, debug=debug)