🏠 Live Flat Rent Price Prediction System

FastAPI Backend → MongoDB Atlas → Power BI Live Dashboard (Scheduled Refresh)

📌 Project Overview

Live_data_Save_mongo_using_Fast_API_backend is an end-to-end machine learning and analytics project focused on flat rent price prediction. The system captures real-time property data through a FastAPI backend, stores it in a cloud MongoDB Atlas database, applies a rent price prediction model, and visualizes insights using a Power BI dashboard with daily scheduled refresh.

This project demonstrates a real-world production workflow combining backend APIs, cloud databases, machine learning predictions, and business intelligence reporting.

🔗 End-to-End Workflow
1️⃣ Data Ingestion (FastAPI Backend)

A FastAPI backend exposes REST endpoints for:

Submitting flat/property details (location, size, bedrooms, amenities, etc.)

Receiving predicted rent prices

Incoming data is validated using Pydantic models

Both raw input data and predicted rent values are processed in real time

2️⃣ Cloud Data Storage (MongoDB Atlas)

All property records and prediction results are stored in MongoDB Atlas (cloud)

Each document includes:

Flat/property features

Predicted rent price

Timestamp (createdAt)

Location and category metadata

MongoDB acts as the single source of truth for analytics

3️⃣ Rent Price Prediction (ML Model)

A trained regression-based ML model predicts flat rent prices

Features include:

Area / city

Flat size (sq ft)

Number of rooms

Furnishing status

Nearby facilities

Model inference is triggered via FastAPI endpoints

Prediction results are saved alongside input data

4️⃣ Data Exposure for Analytics

MongoDB data is accessed for reporting using:

MongoDB Atlas BI / SQL Connector, or

Power BI Web/API connector

Clean, structured data is prepared for BI consumption

5️⃣ Power BI Dashboard (Live Analytics)

Power BI dashboards built using cloud-stored prediction data

Visuals include:

Average rent by city/area

Predicted vs actual rent trends

Price distribution by flat size

Daily and monthly prediction volume

Dashboard published to Power BI Service

6️⃣ Scheduled Refresh (Daily)

Scheduled refresh enabled (daily)

Ensures dashboards stay updated with the latest predictions

Optional gateway configuration if required

No manual intervention needed

🏗️ System Architecture
User / Client App
        ↓
FastAPI Backend (Prediction API)
        ↓
MongoDB Atlas (Cloud Database)
        ↓
Power BI Dataset
        ↓
Power BI Dashboard
        ↓
Daily Scheduled Refresh

🗄️ MongoDB Data Model (Example)

Each document stored includes:

location

flat_size

bedrooms

amenities

predicted_rent

createdAt

This schema enables efficient analytics and dashboarding.

⚙️ Key Technical Highlights

✔️ FastAPI-based production backend
✔️ Real-time ML rent price prediction
✔️ Cloud-native MongoDB Atlas storage
✔️ Clean data pipeline for analytics
✔️ Live Power BI dashboards
✔️ Daily scheduled refresh automation

🧰 Tech Stack
Layer	Technology
Backend API	FastAPI
ML Model	Python (Regression)
Database	MongoDB Atlas (Cloud)
Validation	Pydantic
Analytics	Power BI
Automation	Scheduled Refresh
