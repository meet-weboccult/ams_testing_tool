import pymongo
from constants import HOST, PORT, USERNAME, PASSWORD, DATABASE

class Database:
    def __init__(self) -> None:
        try:
            self.client = pymongo.MongoClient(host=HOST,port=PORT,username=USERNAME,password=PASSWORD)
            self.database = self.client.get_database(DATABASE)    
        except Exception as e:
            print(e)

        self.get_images()    

    def get_images(self):
        totals = set()
        collection = self.database['mobile_usages']
        pipeline = [
    {
        '$group': {
            '_id': '$image', 
            'total_documents': {
                '$sum': 1
            }
        }
    }
]
        groups = collection.aggregate(pipeline)

        print(list(groups))
        # print(totals)  
            
Database()
