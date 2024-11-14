# -*- coding: utf-8 -*-
"""mongoRAG.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Py3dgcuVUMNjo-_W3UZeMWzo2TRkqCnP
"""

!pip install datasets pandas openai pydantic
!pip install "pymongo[srv]"==3.12

import warnings
import os
from google.colab import userdata
mongo_uri = userdata.get('MONGO_URI')
openai_key = userdata.get('OPENAI')
MONGO_URI = mongo_uri
OPENAI_API_KEY = openai_key

from datasets import load_dataset
import pandas as pd
dataset = load_dataset("MongoDB/airbnb_embeddings", streaming=True, split = "train")
dataset = dataset.take(100)
dataset_df = pd.DataFrame(dataset)
dataset_df.head(5)

print(dataset_df.columns)

from typing import List, Optional
from pydantic import BaseModel, ValidationError
from datetime import datetime

class Host(BaseModel):
  host_id : str
  host_url: str
  host_name: str
  host_location: str
  host_about: str
  host_response_time : Optional[str] = None
  host_thumbnail_url : str
  host_picture_url : str
  host_response_rate : Optional[int] = None
  host_is_superhost: bool
  host_has_profile_pic: bool
  host_identity_verified: bool

class Location(BaseModel):
  type : str
  coordinates : List[float]
  is_location_exact: bool

class Address(BaseModel):
  street: str
  government_area: str
  market: str
  country: str
  country_code: str
  location: Location

class Review(BaseModel):
  _id : str
  date: Optional[datetime] = None
  listing_id: str
  reviewer_id: str
  reviewer_name: Optional[str] = None
  comments: Optional[str] = None

class Listing(BaseModel):
  _id: int
  listing_url: str
  name: str
  summary: str
  space: str
  description: str
  neighborhood_overview: Optional[str] = None
  notes: Optional[str] = None
  transit: Optional[str] = None
  access: str
  interaction: Optional[str] = None
  house_rules: str
  property_type: str
  room_type: str
  bed_type: str
  minimum_nights: int
  maximum_nights: int
  cancellation_policy: str
  last_scraped: Optional[datetime] = None
  calendar_last_scraped: Optional[datetime] = None
  first_review: Optional[datetime] = None
  last_review: Optional[datetime] = None
  accommodates: int
  bedrooms: Optional[float] = 0
  beds: Optional[float] = 0
  number_of_reviews: int
  bathrooms: Optional[float] = 0
  amenities: List[str]
  price: int
  security_deposit: Optional[float] = None
  cleaning_fee: Optional[float] = None
  extra_people: int
  guests_included: int
  images: dict
  host: Host
  address: Address
  availability: dict
  review_scores: dict
  reviews: List[Review]
  text_embeddings: List[float]

records = dataset_df.to_dict(orient = 'records')
for record in records:
  for key, value in record.items():
    if isinstance(value, list):
      processed_list = [None if pd.isnull(v) else v for v in value]
      record[key] = processed_list
    else:
      if pd.isnull(value):
        record[key] = None

try:
  listings = [Listing(**record).dict() for record in records]
  print(listings[0].keys())
except ValidationError as e:
  print(e)

from pymongo.mongo_client import MongoClient
from pymongo.operations import SearchIndexModel
database_name = "airbnb_dataset"
collection_name = "listings_reviews"

def get_mongo_client(mongo_uri):
  client = MongoClient(mongo_uri, appname ="devrel")
  print("Connection to MongoDB Successful")
  return client

mongo_client = get_mongo_client(MONGO_URI)
db = mongo_client.get_database(database_name)
collection = db.get_collection(collection_name)

collection.delete_many({})

collection.insert_many(listings)
print("Data Ingestion into Mongo Complete")

