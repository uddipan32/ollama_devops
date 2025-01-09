from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class ConnectMongoDB:
    def __init__(self, uri: str):
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # 5 second timeout
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client.get_database("ollame_devops")
            self.endpoints_collection = self.db.get_collection("endpoints")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")

    def get_endpoints(self):
        return self.endpoints_collection.find()

    def add_endpoint(self, endpoint: dict):
        self.endpoints_collection.insert_one({
            "name": endpoint["name"],
            "url": endpoint["url"],
            "method": endpoint["method"],
            "headers": endpoint["headers"],
            "body": endpoint["body"],
        })

    def delete_endpoint(self, endpoint_id: str):
        self.endpoints_collection.delete_one({"_id": endpoint_id})

    def update_endpoint(self, endpoint_id: str, endpoint: dict):
        self.endpoints_collection.update_one({"_id": endpoint_id}, {"$set": endpoint})

