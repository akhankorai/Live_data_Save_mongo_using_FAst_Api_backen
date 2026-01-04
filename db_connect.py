from pymongo import MongoClient
import os

MONGO_URI = "mongodb+srv://ijaz:1111@cluster0.bh8gimu.mongodb.net/?appName=Cluster0&retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)

db = client["powerbidata"]
collection = db["powerbidata"]

doc = collection.find_one()

required_fields = [
    "amenities", "bathrooms", "bedrooms", "square_feet",
    "cityname", "state", "latitude", "longitude",
    "geo_cluster", "amenity_group"
]

print("Checking document:", doc["_id"])

missing = [f for f in required_fields if f not in doc]

if missing:
    print("Missing fields:", missing)
else:
    print("All required fields exist")

# type checks
assert isinstance(doc["bathrooms"], (int, float))
assert isinstance(doc["bedrooms"], (int, float))
assert isinstance(doc["square_feet"], int)
assert isinstance(doc["geo_cluster"], int)

print("Type checks passed")
