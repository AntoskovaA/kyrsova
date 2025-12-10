"""
Модуль маршрутів Flask
"""
from .main import main_bp
from .graph import graph_bp
from .search import search_bp

__all__ = ['main_bp', 'graph_bp', 'search_bp']