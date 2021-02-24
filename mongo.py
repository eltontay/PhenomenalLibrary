import pymongo

client = pymongo.MongoClient("mongodb+srv://admin:admin@phenomcluster.1j72v.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client["phenomLibrary"]
collection = db["libraryBooks"]

