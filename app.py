from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, computed_field
from typing import Optional
import pandas as pd
import numpy as np
import pickle
import joblib
from db import predictions_col
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


kmeans = joblib.load("geo_cluster_kmeans.pkl")


from catboost import CatBoostRegressor

cat_model = CatBoostRegressor()
cat_model.load_model("catboost_price_model.cbm")



 
VALID_AMENITIES = [
    "Other", "Parking", "Parking,Storage", "Gym,Pool", "Pool",
    "Gym,Parking,Pool", "Parking,Pool", "Washer Dryer", "Patio/Deck",
    "Clubhouse,Gym,Pool", "Gym", "Parking,Patio/Deck,Storage",
    "Wood Floors", "Parking,Washer Dryer", "Gym,Patio/Deck,Pool",
    "Dishwasher,Refrigerator", "Gym,Parking,Pool,Storage",
    "Refrigerator", "Parking,Patio/Deck", "Clubhouse,Gym,Parking,Pool",
    "Parking,Wood Floors", "Cable or Satellite,TV", "Storage"
]
VALID_CITIES = [
    "Other",
    "Dallas", "Denver", "Los Angeles", "Las Vegas", "Arlington", "Atlanta",
    "Charlotte", "Austin", "San Antonio", "Raleigh", "Richmond", "Alexandria",
    "Houston", "Cincinnati", "San Diego", "Tampa", "Colorado Springs",
    "Chicago", "Columbus", "Kansas City", "Omaha", "Cleveland", "Norfolk",
    "Boston", "Tucson", "Marietta", "Jersey City", "Greensboro"
]

VALID_STATE = [
    "Other", "TX", "CA", "VA", "NC", "CO", "FL", "MD", "OH", "MA",
    "GA", "NJ", "WA", "NV", "AZ", "MO", "LA", "IL", "PA", "TN", "NE"
]


def map_amenity(a: Optional[str]) -> str:
    a = str(a) 
    has_parking = "Parking" in a
    has_gym     = "Gym" in a
    has_pool    = "Pool" in a
    has_laundry = ("Washer" in a) or ("Dryer" in a) or ("Laundry" in a)
    has_storage = "Storage" in a

    if has_parking and (has_gym or has_pool):
        return "Parking + Gym/Pool"
    elif has_parking:
        return "Parking"
    elif has_gym or has_pool:
        return "Gym/Pool"
    elif has_laundry:
        return "Laundry"
    elif has_storage:
        return "Storage"
    else:
        return "Other"


def map_pets_value(v: Optional[str]) -> int:
    if v is None:
        return 0
    v = str(v).strip()
    mapping = {"no": 0, "yes": 1, "Cats": 1, "Dogs": 1}
    return mapping.get(v, 0)


# Pydantic Model
class Listing(BaseModel):
    amenities: Optional[str] = None
    pets_allowed: Optional[str] = None
    cityname: Optional[str] = None
    state: Optional[str] = None

    bathrooms: float
    bedrooms: float
    fee: int
    has_photo: int
    square_feet: int
    latitude: float
    longitude: float

    @field_validator("square_feet", mode="before")
    @classmethod
    def bucket_square_feet(cls, v):
        try:
            x = float(v)
        except Exception:
            return -1

        if x <= 500:
            return 0
        elif x <= 700:
            return 1
        elif x <= 900:
            return 2
        elif x <= 1100:
            return 3
        elif x <= 1300:
            return 4
        elif x <= 1500:
            return 5
        else:
            return 6

    @field_validator("bathrooms", mode="before")
    @classmethod
    def bucket_bathrooms(cls, v):
        try:
            b = float(v)
        except Exception:
            return 1  

        if b <= 1:
            return 1
        elif b <= 2:
            return 2
        elif b <= 3:
            return 3
        elif b <= 4:
            return 4
        else:
            return 5

    @field_validator("bedrooms", mode="before")
    @classmethod
    def bucket_bedrooms(cls, v):
        try:
            b = float(v)
        except Exception:
            return 1  

        if b <= 1:
            return 1
        elif b <= 2:
            return 2
        elif b <= 3:
            return 3
        elif b <= 4:
            return 4
        elif b <= 5:
            return 5
        elif b <= 6:
            return 6
        else:
            return 7

    @field_validator("amenities")
    @classmethod
    def validate_amenities(cls, v):
        if v is None:
            return None
        v = v.strip()
        return v if v else None

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        if v is None:
            return v
        v = v.strip().upper()
        if v not in VALID_STATE:
            raise ValueError(f"Invalid state '{v}'. Allowed: {VALID_STATE}")
        return v

    @field_validator("cityname")
    @classmethod
    def validate_cityname(cls, v):
        if v is None:
            raise ValueError("cityname is required")
        v = v.strip()
        if not v:
            raise ValueError("cityname cannot be empty")
        if v not in VALID_CITIES:
            raise ValueError(f"Invalid city '{v}'. Allowed: {VALID_CITIES}")
        return v

    @computed_field
    @property
    def amenity_group(self) -> str:
        return map_amenity(self.amenities)

    @computed_field
    @property
    def pets_allowed_num(self) -> int:
        return map_pets_value(self.pets_allowed)

    @computed_field
    @property
    def bath_bed_ratio(self) -> float:
        return self.bathrooms / (self.bedrooms + 1)

    @computed_field
    @property
    def total_rooms(self) -> float:
        return self.bedrooms + self.bathrooms

    @computed_field
    @property
    def bed_sqft_interaction(self) -> float:
        return self.bedrooms * self.square_feet

    @computed_field
    @property
    def bath_sqft_interaction(self) -> float:
        return self.bathrooms * self.square_feet


feature_cols = [
    "fee",
    "has_photo",
    "pets_allowed",      
    "cityname",
    "state",
    "geo_cluster",
    "amenity_group",
    "bath_bed_ratio",
    "total_rooms",
    "bed_sqft_interaction",
    "bath_sqft_interaction",
    "longitude",
    "square_feet",
    "latitude",
    "bathrooms",
    "bedrooms",
]


app = FastAPI(
    title="Rental Price Prediction API",
    version="1.0.0",
    description="FastAPI service for predicting apartment rent price."
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        
    allow_credentials=True,
    allow_methods=["*"],      
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict_rent(payload: Listing):
    try:
        logger.info(" Received /predict request")

        data = payload.model_dump()
        logger.info(f"Payload data: {data}")

        df = pd.DataFrame([data])

        df["pets_allowed"] = df["pets_allowed_num"]
        df.drop(columns=["pets_allowed_num"], inplace=True, errors="ignore")

        df["geo_cluster"] = kmeans.predict(df[["latitude", "longitude"]])

        X = df[feature_cols]

        pred_log = float(cat_model.predict(X)[0])
        pred_price = float(np.expm1(pred_log))

        record = {
            **data,
            "pets_allowed": int(df["pets_allowed"].iloc[0]),
            "geo_cluster": int(df["geo_cluster"].iloc[0]),
            "predicted_log_price": pred_log,
            "predicted_price": pred_price,
            "created_at": datetime.now(timezone.utc)
        }

        result = predictions_col.insert_one(record)

        logger.info(f"Data stored successfully. MongoDB _id={result.inserted_id}")

        return {
            "predicted_price": pred_price,
            "predicted_log_price": pred_log,
            "saved_id": str(result.inserted_id)
        }

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))