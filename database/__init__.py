"""
Модуль для роботи з базою даних
"""
from .mongo_client import MongoDB
from .models import Graph, SearchResult

__all__ = ['MongoDB', 'Graph', 'SearchResult']