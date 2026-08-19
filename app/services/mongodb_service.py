from pymongo import MongoClient
from pymongo.database import Database
from app.config.settings import settings

class MongoDBService:
    client: MongoClient = None
    db: Database = None

    @classmethod
    def connect_db(cls):
        """Establish connection to MongoDB Atlas."""
        if cls.client is None:
            if not settings.MONGO_URI:
                raise ValueError("MONGO_URI is not set in environment variables or .env file.")
            
            # PyMongo automatically handles TLS/SSL for mongodb+srv:// URIs used by Atlas
            cls.client = MongoClient(settings.MONGO_URI)
            cls.db = cls.client[settings.DB_NAME]
            
            # Ping the server to verify connection success
            cls.client.admin.command('ping')
            print(f" Successfully connected to MongoDB Atlas: {settings.DB_NAME}")

    @classmethod
    def close_db(cls):
        """Close MongoDB Atlas connection."""
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None
            print("❌ Closed MongoDB Atlas connection.")

    @classmethod
    def get_db(cls) -> Database:
        """Get database instance."""
        if cls.db is None:
            cls.connect_db()
        return cls.db

# Convenience shortcuts for collections
def get_users_collection():
    return MongoDBService.get_db()["users"]

def get_profiles_collection():
    return MongoDBService.get_db()["profiles"]

def get_trips_collection():
    return MongoDBService.get_db()["trips"]

def get_itineraries_collection():
    return MongoDBService.get_db()["itineraries"]