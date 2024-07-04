
import time 
import logging 
import pymongo 
import json 

#This test gives you the count for each collection in each database
#As well as the last two records in the database 

n = 2 
client = pymongo.MongoClient("127.0.0.1:27017")
print("---------Local Mongo Database Report--------------")
#First, print the database names 
print("All Databases")
print(client.database_names())
for database in client.database_names():
    if database == "admin" or database == "config" or database == "local":
        continue
    try:
        print(f"Database: {database}")
        db = getattr(client, database)
        print("Collections")
        collections = list(db.collection_names())
        print(collections)
        for collection_name in collections: 
            try:
                print(f"Collection Name {collection_name}")
                col = getattr(db, collection_name)
                num_docs = col.find().count()
                print(f"Number of Documents {num_docs}")
                #last_n_docs = col.find().sort({"_id", 1}).limit(n)
                last_n_docs = col.find().skip(col.count() - n)
                print(f"Last {n} Documents:")
                for doc in last_n_docs:
                    print_doc = json.dumps(doc, indent=4, default=str)
                    print(print_doc)
            except Exception as e:
                print(f"Could not report on collection {collection_name}; {e}")
    except Exception as e:
        print(f"Could not report on database {database}; {e}")

client.close()

