"""
Клієнт для роботи з MongoDB
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, PyMongoError
from bson.objectid import ObjectId
from datetime import datetime
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """
    Клас для взаємодії з MongoDB.
    Реалізує методи для підключення, ініціалізації індексів, а також 
    CRUD-операцій з графами та результатами пошуку.
    """
    
    def __init__(self, uri: str, database: str):
        """
        Ініціалізація підключення до MongoDB.
        
        Args:
            uri: URI для підключення до MongoDB.
            database: Назва бази даних.
        """
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            # Перевірка з'єднання
            self.client.admin.command('ping')
            self.db = self.client[database]
            logger.info(f"Підключено до MongoDB: {database}")
            self._create_indexes()
        except ConnectionFailure as e:
            logger.error(f" Помилка підключення до MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Створення індексів для оптимізації запитів"""
        try:
            # Індекси для графів
            self.db.graphs.create_index([("name", ASCENDING)])
            self.db.graphs.create_index([("created_at", DESCENDING)])
            
            # Індекси для результатів пошуку
            self.db.search_results.create_index([("graph_id", ASCENDING)])
            self.db.search_results.create_index([("timestamp", DESCENDING)])
            self.db.search_results.create_index([
                ("graph_id", ASCENDING),
                ("algorithm", ASCENDING),
                ("start", ASCENDING),
                ("end", ASCENDING)
            ])
            
            logger.info("Індекси створено")
        except PyMongoError as e:
            logger.warning(f"⚠️ Помилка створення індексів: {e}")
    
    # === ОПЕРАЦІЇ З ГРАФАМИ ===
    
    def create_graph(self, graph_data: Dict) -> str:
        """
        Створення нового графа у колекції 'graphs'.
        
        Args:
            graph_data: Дані графа (name, nodes, edges).
            
        Returns:
            ID створеного графа у вигляді рядка.
        """
        try:
            # Створюємо копію, щоб не змінювати оригінальний словник
            data_to_insert = graph_data.copy()
            data_to_insert['created_at'] = datetime.utcnow()
            result = self.db.graphs.insert_one(data_to_insert)
            logger.info(f"Граф створено: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f" Помилка створення графа: {e}")
            raise
    
    def get_graph(self, graph_id: str) -> Optional[Dict]:
        """
        Отримання графа за ID.
        
        Args:
            graph_id: ID графа (рядок).
            
        Returns:
            Дані графа у вигляді словника з ID-рядком або None, якщо не знайдено.
        """
        try:
            graph = self.db.graphs.find_one({"_id": ObjectId(graph_id)})
            if graph:
                # Конвертуємо ObjectId у рядок для JSON-серіалізації
                graph['_id'] = str(graph['_id'])
            return graph
        except PyMongoError as e:
            logger.error(f"Помилка отримання графа: {e}")
            return None
    
    def get_all_graphs(self, limit: int = 50, skip: int = 0) -> List[Dict]:
        """
        Отримання списку всіх графів, відсортованих за датою створення.
        
        Args:
            limit: Максимальна кількість результатів.
            skip: Кількість записів для пропуску.
            
        Returns:
            Список графів.
        """
        try:
            graphs = list(self.db.graphs.find()
                         .sort("created_at", DESCENDING)
                         .limit(limit)
                         .skip(skip))
            
            for graph in graphs:
                # Конвертуємо ObjectId у рядок
                graph['_id'] = str(graph['_id'])
            
            return graphs
        except PyMongoError as e:
            logger.error(f"Помилка отримання графів: {e}")
            return []
    
    def update_graph(self, graph_id: str, update_data: Dict) -> bool:
        """
        Оновлення графа за ID.
        
        Args:
            graph_id: ID графа.
            update_data: Нові дані для оновлення.
            
        Returns:
            True якщо успішно, False інакше.
        """
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.db.graphs.update_one(
                {"_id": ObjectId(graph_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Помилка оновлення графа: {e}")
            return False
    
    def delete_graph(self, graph_id: str) -> bool:
        """
        Видалення графа та всіх пов'язаних результатів пошуку.
        
        Args:
            graph_id: ID графа.
            
        Returns:
            True якщо успішно, False інакше.
        """
        try:
            # Видалення пов'язаних результатів (імітація каскадного видалення)
            self.db.search_results.delete_many({"graph_id": ObjectId(graph_id)})
            
            # Видалення графа
            result = self.db.graphs.delete_one({"_id": ObjectId(graph_id)})
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"Помилка видалення графа: {e}")
            return False
    
    # === ОПЕРАЦІЇ З РЕЗУЛЬТАТАМИ ПОШУКУ ===
    
    def save_search_result(self, result_data: Dict) -> str:
        """
        Збереження результату пошуку у колекції 'search_results'.
        
        Args:
            result_data: Дані результату (включаючи graph_id).
            
        Returns:
            ID збереженого результату у вигляді рядка.
        """
        try:
            result_data['timestamp'] = datetime.utcnow()
            # Конвертуємо graph_id у ObjectId для зберігання зв'язку
            result_data['graph_id'] = ObjectId(result_data['graph_id'])
            
            result = self.db.search_results.insert_one(result_data)
            logger.info(f"Результат збережено: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Помилка збереження результату: {e}")
            raise
    
    def get_search_result(self, result_id: str) -> Optional[Dict]:
        """
        Отримання результату пошуку за ID.
        
        Args:
            result_id: ID результату.
            
        Returns:
            Дані результату або None.
        """
        try:
            result = self.db.search_results.find_one({"_id": ObjectId(result_id)})
            if result:
                # Конвертуємо ObjectId у рядок
                result['_id'] = str(result['_id'])
                result['graph_id'] = str(result['graph_id'])
            return result
        except PyMongoError as e:
            logger.error(f" Помилка отримання результату: {e}")
            return None
    
    def get_graph_results(self, graph_id: str, limit: int = 20) -> List[Dict]:
        """
        Отримання всіх результатів пошуку для конкретного графа.
        
        Args:
            graph_id: ID графа.
            limit: Максимальна кількість результатів.
            
        Returns:
            Список результатів.
        """
        try:
            results = list(self.db.search_results.find(
                {"graph_id": ObjectId(graph_id)}
            ).sort("timestamp", DESCENDING).limit(limit))
            
            for result in results:
                # Конвертуємо ObjectId у рядок
                result['_id'] = str(result['_id'])
                result['graph_id'] = str(result['graph_id'])
            
            return results
        except PyMongoError as e:
            logger.error(f"❌ Помилка отримання результатів: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """
        Отримання загальної статистики системи (кількість графів, пошуків, 
        використання алгоритмів).
        
        Returns:
            Словник зі статистикою.
        """
        try:
            # Використання конвеєра агрегації для аналітики
            stats = {
                'total_graphs': self.db.graphs.count_documents({}),
                'total_searches': self.db.search_results.count_documents({}),
                'algorithms_usage': list(self.db.search_results.aggregate([
                    {"$group": {
                        "_id": "$algorithm",
                        "count": {"$sum": 1},
                        "avg_time": {"$avg": "$execution_time"}
                    }}
                ]))
            }
            return stats
        except PyMongoError as e:
            logger.error(f"Помилка отримання статистики: {e}")
            return {}
    
    def close(self):
        """Закриття з'єднання з MongoDB"""
        self.client.close()
        logger.info(" З'єднання з MongoDB закрито")