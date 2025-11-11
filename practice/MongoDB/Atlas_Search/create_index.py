from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
import os 
from dotenv import load_dotenv
load_dotenv()

# connect to your Atlas deployment
uri = os.getenv("MONGO_URI")
client = MongoClient(uri)

# set namespace
database = client["sample_mflix"]
collection = database["movies"]

# define your MongoDB Search index
search_index_model = SearchIndexModel(
    definition={
        "mappings": {
            "dynamic": True
        },
    },
    name="default",
)

# create the index
result = collection.create_search_index(model=search_index_model)
print(result)
