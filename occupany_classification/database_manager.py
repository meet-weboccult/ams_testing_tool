from datetime import datetime
import pymongo

class Database_data:
    def __init__(self,validator_name) -> None:
        self.validator_name = validator_name
        self.mongo_connection_url = "mongodb://localhost:27017/"

    def connection(self):
        client = pymongo.MongoClient(self.mongo_connection_url)
        db = client["people-occupancy"]
        self.collection = db["occupancy"]

    def find_all_data(self):
        self.x = self.collection.find()

    def get_data(self):
        return self.x

    def find_unique(self, name):
        self.name = self.collection.distinct(name)
        return self.name

    def get_workspace_name(self, site_name):
        workspace_name = self.collection.find(
            {"site_name": site_name}, {"workspace_name": 1, "_id": 0}
        ).distinct("workspace_name")
        return workspace_name

    def get_image(self, filter):
        pipeline = [
            {
                "$match": {
                    "site_name": filter["office"],
                    "workspace_name": filter["floor"],
                    "event_time": {
                        "$gte": datetime.fromisoformat(filter["start_time"]),
                        "$lte": datetime.fromisoformat(filter["end_time"]),
                    },
                    "validated_by": {"$exists": False},
                }
            },
            {
                # Group by image and get all document in the group
                "$group": {"_id": "$image", "documents": {"$push": "$$ROOT"}}
            },
        ]
        data = self.collection.aggregate(pipeline)
        list_data = list(data)
        return list_data
    def update_date(self, id,status):
        self.collection.update_one({"_id": id}, {"$set": {"validated_by": self.validator_name,"is_occupancy_correct":status}})

