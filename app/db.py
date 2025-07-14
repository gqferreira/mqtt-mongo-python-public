from pymongo import MongoClient
import app.config as config

client = MongoClient(config.MONGODB_URI)
db = client[config.MONGODB_DB]
print(f'Connected to MongoDB [{ config.MONGODB_DB }]')