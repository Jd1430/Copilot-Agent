from pymongo import MongoClient
from app.config import get_secret
import json

mongo_uri = get_secret("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["myDatabase"]
collection = db["users"]

def run_mongo_query(query_str):
    import json

    try:
        # Clean and parse query
        query_str = query_str.strip()
        if query_str.startswith("```"):
            query_str = query_str.strip("`").replace("json", "").strip()

        query_obj = json.loads(query_str)

        # If it's a read (normal dict), run find
        if isinstance(query_obj, dict) and "operation" not in query_obj:
            results = list(collection.find(query_obj, {"_id": 0}))
            return results

        # Handle insert/update/delete
        elif isinstance(query_obj, dict) and "operation" in query_obj:
            op = query_obj["operation"]
            q = query_obj["query"]

            if op == "insert":
                result = collection.insert_one(q)
                return [f"Inserted document ID: {str(result.inserted_id)}"]
            elif op == "update":
                result = collection.update_many(q["filter"], {"$set": q["update"]})
                return [f"Updated {result.modified_count} documents."]
            elif op == "delete":
                result = collection.delete_many(q)
                return [f"Deleted {result.deleted_count} documents."]
            else:
                return [f"Unsupported operation: {op}"]
        else:
            return ["Unrecognized query format."]
    except Exception as e:
        return [f"Error executing query: {e}"]


