from pprint import pprint
from pymongo import MongoClient
from bson import json_util

class Model:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["people-occupancy"]
        self.collection = self.db["mobile_usages"]
        self.documents = []
        self.current_document_index = 0
        self.bbox_mappings = {}

    def load_documents_from_mongodb(self, start_date, end_date, site_name, workspace_name):
        
        self.documents = []
        pipeline = [
            {"$match": {
                "start_time": {"$gte": start_date, "$lte": end_date},
                "site_name": site_name,
                "workspace_name": workspace_name,
                "validated_by" : {"$exists":False}
            }},
            {"$group": {
                "_id": "$image",
                "documents": {"$push": "$$ROOT"}
            }},
            {
                "$sort": {
                    "documents.start_time": 1
                }
            }
        ]
        self.documents = list(self.collection.aggregate(pipeline))

    def get_current_document(self):
        if self.documents:
            return self.documents[self.current_document_index]['documents']

    def get_image_url(self):
        if self.documents:
            return self.get_current_document()[0].get("image", None)

    def get_image_data(self):
        return json_util.dumps(self.get_current_document(), indent=8)

    def get_bboxes(self):
        
        current_document = self.get_current_document()
        result = []

        for item in current_document:
            result.append(item['img_data']['phone_results'][0]['bbox'])
        
        return result

    def previous_image(self):

        if self.current_document_index > 0:
            self.current_document_index -= 1
            return True

    def next_image(self):

        if self.current_document_index < len(self.documents) - 1:
            self.current_document_index += 1
            return True