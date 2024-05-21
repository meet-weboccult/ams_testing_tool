import pymongo
from bson.objectid import ObjectId
from datetime import datetime
from .constants import HOST, PORT, USERNAME, PASSWORD, DATABASE
class Database:
    _instance = None
    @staticmethod
    def get_instance():
        return Database._instance

    def __init__(self,validator_name) -> None:
        if Database._instance is not None:
            return
        else:
            Database._instance = self

        try:
            self.client = pymongo.MongoClient("mongodb://localhost:27017/")
            self.database = self.client.get_database(DATABASE)    
            self.validator_name = validator_name
        except Exception as e:
            print(e)

    def get_site_names(self):
        collection = self.database['mobile_usages']
        site_names = collection.distinct("site_name")
        return site_names
    
    def get_workspace_of_site(self,site_name):
        collection = self.database['mobile_usages']
        workspaces = collection.find({"site_name":site_name},{"workspace_name":1,"_id":0}).distinct("workspace_name")
        return workspaces
    
    def get_images(self,filter):
        collection = self.database['mobile_usages']
        pipeline = [
            {
                "$match": {
                    "site_name": filter['office'],
                    "workspace_name": filter['floor'],
                    "start_time": {
                        "$gte": datetime.fromisoformat(filter['start_time']),
                        "$lte": datetime.fromisoformat(filter['end_time'])
                    },
                    "validated_by":{"$exists":False}
                }
            },
            {
                # Group by image and get all document in the group 
                "$group": {
                    "_id": "$image",
                    "documents": {
                        "$push": "$$ROOT"
                    }
                }
            },
            
        ]
        data = collection.aggregate(pipeline)
        return data
            
    def update_bbox(self,document):
        object_id = ObjectId(document['_id'])
        collection = self.database['mobile_usages']
        collection.update_one({"_id":object_id},{"$set":document})

    def delete_bbox(self,document):
        object_id = ObjectId(document['_id'])
        collection = self.database['mobile_usages']
        collection.delete_one({"_id":object_id})
    
    def approve_image(self,image_id):
        collection = self.database['mobile_usages']
        # TODO : change validated_by on integration of all modules
        result = collection.update_many({"image":image_id},
                               {"$set":{"is_correct":True,"validated_by":self.validator_name}})
        return result.modified_count
    
    def reject_image(self,data,new_bboxes):
        image = data['image']
        # TODO : change validated_by on integration of all modules

        collection = self.database['mobile_usages']
        result = collection.update_many({"image":image},
                               {"$set":{"is_correct":False,"validated_by":self.validator_name}})
        
        if len(new_bboxes) == 0:
            return result.acknowledged
        
        new_document = {
            "workspace_name" : data['workspace_name'],
            "site_name" : data['site_name'],
            'image'  : data['image'],
            'bboxes' : new_bboxes,
        }
        if 'camera_name' in data:
            new_document['camera_name'] = data['camera_name']        

        collection = self.database['corrected_mobiles']
        result = collection.insert_one(new_document)
        return result.acknowledged
        
    