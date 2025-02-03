import json
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
from pydantic import BaseModel
from extraction_service import ContractDataExtractionService
from api_rates import UPSApiRates  # Import UPSApiRates class from ups_api.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Load dummy data from JSON file
def load_dummy_data():
    with open("constants/dummyData.json", "r") as file:
        return json.load(file)

DUMMY_DATA = load_dummy_data()  # Load dummy data

# FastAPI setup
app = FastAPI()

# Allow CORS from all origins
app.add_middleware(CORSMiddleware, allow_origins=["*"])

class DiscountInput(BaseModel):
    weekly_price: float
    zone: str

@app.get("/")
async def read_root():
    return JSONResponse(content={"success": True, "message": "Server is running"})

@app.post("/api/extract")
async def extract(file: UploadFile = File(...)):
    extracted_data = ContractDataExtractionService.extract(file)
    return JSONResponse(content={"success": True, "message": "Extracted data", "tables": extracted_data})

# Helper function to get portfolio tier incentive based on weekly price
def get_portfolio_tier_incentive(weekly_price: float):
    for tier in DUMMY_DATA["tables"]:
        if tier["table_type"] == "portfolio_tier_incentives":
            for row in tier["data"]:
                band = row["band"].split(" - ")
                lower_bound = float(band[0].replace(",", ""))
                upper_bound = float(band[1].replace(",", ""))
                if lower_bound <= weekly_price <= upper_bound:
                    return abs(float(row["incentive"].strip('%')))
    return 0

# Helper function to get service incentive for a given service name
def get_service_incentive(service_name: str):
    for tier in DUMMY_DATA["tables"]:
        if tier["table_type"] == "service_incentives":
            for row in tier["data"]:
                if row["service"] == service_name:
                    incentive_str = row["incentive"].strip('%')
                    incentive_value = re.sub(r'[^0-9.]', '', incentive_str)
                    return abs(float(incentive_value))
    return 0

# Helper function to get zone incentive based on zone and service name
def get_zone_incentive(service_name: str, zone: str):
    for tier in DUMMY_DATA["tables"]:
        if tier["table_type"] == "zone_incentive":
            for row in tier["data"]:
                if row["zone"] == zone and service_name in row["service"]:
                    return abs(float(row["incentive"].strip('%')))
    return 0

@app.post("/calculate_discount")
async def calculate_discount(input_data: DiscountInput):
    weekly_price = input_data.weekly_price
    zone = input_data.zone

    # Step 1: Get Service Rates (fetch from UPS API)
    ups_api = UPSApiRates()
    rates = ups_api.get_rates(weight=weekly_price, zone=zone)
    
    if not rates:
        return JSONResponse(status_code=404, content={"error": "No rates found from UPS API"})

    # Print the API response for debugging
    print("UPS API Response:", rates)

    # Example: Fetch the first available rate
    service_name = rates[0]["serviceLevel"]
    base_rate = float(rates[0]["amount"])

    # Step 2: Apply Portfolio Tier Incentive to the base amount
    portfolio_incentive = get_portfolio_tier_incentive(weekly_price)
    portfolio_discounted_amount = base_rate * (1 - portfolio_incentive / 100)

    # Step 3: Apply Service Incentives on the portfolio discounted amount
    service_incentives = []
    for tier in DUMMY_DATA["tables"]:
        if tier["table_type"] == "service_incentives":
            for row in tier["data"]:
                service_incentive = get_service_incentive(row["service"])
                service_discounted_amount = portfolio_discounted_amount * (1 - service_incentive / 100)
                service_incentives.append({
                    "service_name": row["service"],
                    "portfolio_incentive_applied": f"{portfolio_incentive}%",
                    "service_incentive_applied": f"{service_incentive}%",
                    "discounted_amount": round(service_discounted_amount, 2)
                })

    # Step 4: Get Zone Incentive and apply it to the base amount
    zone_incentive = get_zone_incentive(service_name, zone)
    zone_incentive_applied = zone_incentive
    zone_incentive_amount = base_rate * (1 - zone_incentive / 100)

    # Step 5: Final Amount Logic: If the discounted amount exceeds the zone incentive, use zone incentive amount as final amount
    final_amount = service_discounted_amount
    if service_discounted_amount < zone_incentive_amount:
        final_amount = zone_incentive_amount

    # Return the results, correctly iterating over service_incentives
    return [{
        "service_name": service_incentive["service_name"],
        "portfolio_incentive_applied": service_incentive["portfolio_incentive_applied"],
        "service_incentive_applied": service_incentive["service_incentive_applied"],
        "discounted_amount": service_incentive["discounted_amount"],
        "zone_incentive_applied": f"{zone_incentive_applied}%",
        "zone_incentive_amount": round(zone_incentive_amount, 2),
        "final_amount": round(final_amount, 2)
    } for service_incentive in service_incentives]  # Fixing iteration over list













# import json
# import re
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from fastapi import File, UploadFile
# from pydantic import BaseModel
# from extraction_service import ContractDataExtractionService


# # Load dummy data from JSON file
# def load_dummy_data():
#     with open("constants/dummyData.json", "r") as file:
#         return json.load(file)

# DUMMY_DATA = load_dummy_data()  # Load dummy data


# class DiscountInput(BaseModel):
#     weekly_price: float
#     base_amount: float
#     zone: str


# app = FastAPI()

# # Allow CORS from all origins
# app.add_middleware(CORSMiddleware, allow_origins=["*"])


# @app.get("/")
# async def read_root():
#     return JSONResponse(content={"success": True, "message": "Server is running"})


# @app.post("/api/extract")
# async def extract(file: UploadFile = File(...)):
#     extracted_data = ContractDataExtractionService.extract(file)
#     return JSONResponse(content={"success": True, "message": "Extracted data", "tables": extracted_data})


# # Function to extract incentives from dummy data
# def extract_incentives(dummy_data):
#     zone_incentives = []
#     service_incentives = []
#     portfolio_incentives = []

#     for table in dummy_data["tables"]:
#         if table["table_type"] == "weight_zone_incentive":
#             for row in table["data"]:
#                 zone_incentives.append({
#                     "zone": row["zone"],
#                     "incentive": abs(float(row["incentive"].strip('%')))
#                 })
        
#         if table["table_type"] == "service_incentives":
#             for row in table["data"]:
#                 service_incentives.append({
#                     "service": row["service"],
#                     "incentive": abs(float(row["incentive"].strip('%')))
#                 })
        
#         if table["table_type"] == "portfolio_tier_incentives":
#             for row in table["data"]:
#                 band = row["band"].split(" - ")
#                 lower_bound = float(band[0].replace(",", ""))
#                 upper_bound = float(band[1].replace(",", ""))
#                 portfolio_incentives.append({
#                     "service": row["service"],
#                     "land_zone": row["land/zone"],
#                     "band": {"lower_bound": lower_bound, "upper_bound": upper_bound},
#                     "incentive": abs(float(row["incentive"].strip('%')))
#                 })

#     return {
#         "zone_incentives": zone_incentives,
#         "service_incentives": service_incentives,
#         "portfolio_incentives": portfolio_incentives
#     }


# # Helper function to get portfolio tier incentive based on weekly price
# def get_portfolio_tier_incentive(weekly_price: float):
#     for tier in DUMMY_DATA["tables"]:
#         if tier["table_type"] == "portfolio_tier_incentives":
#             for row in tier["data"]:
#                 band = row["band"].split(" - ")
#                 lower_bound = float(band[0].replace(",", ""))
#                 upper_bound = float(band[1].replace(",", ""))
#                 if lower_bound <= weekly_price <= upper_bound:
#                     return abs(float(row["incentive"].strip('%')))
#     return 0


# # Helper function to get service incentive for a given service name
# def get_service_incentive(service_name: str):
#     for tier in DUMMY_DATA["tables"]:
#         if tier["table_type"] == "service_incentives":
#             for row in tier["data"]:
#                 if row["service"] == service_name:
#                     # Remove unnecessary text and convert to positive
#                     incentive_str = row["incentive"].strip('%')
#                     incentive_value = re.sub(r'[^0-9.]', '', incentive_str)
#                     return abs(float(incentive_value))  # Return positive value
#     return 0

# # Helper function to get zone incentive for a given zone
# def get_zone_incentive(zone: str):
#     # Loop through the tables to find the zone_incentive table
#     for tier in DUMMY_DATA["tables"]:
#         if tier["table_type"] == "zone_incentive":  # We are looking for the zone_incentive table
#             for row in tier["data"]:
#                 if row["zone"] == zone:  # Check if the zone matches
#                     # Return the incentive value as a positive percentage
#                     return abs(float(row["incentive"].strip('%')))
#     return 0  # If the zone is not found, return 0


# @app.post("/calculate_discount")
# async def calculate_discount(input_data: DiscountInput):
#     weekly_price = input_data.weekly_price
#     base_amount = input_data.base_amount
#     zone = input_data.zone

#     # Step 1: Apply Portfolio Tier Incentive to the base amount
#     portfolio_incentive = get_portfolio_tier_incentive(weekly_price)
#     portfolio_discounted_amount = base_amount * (1 - portfolio_incentive / 100)

#     # Step 2: Apply Service Incentives on the portfolio discounted amount
#     service_incentives = []
#     for tier in DUMMY_DATA["tables"]:
#         if tier["table_type"] == "service_incentives":
#             for row in tier["data"]:
#                 service_incentive = get_service_incentive(row["service"])
#                 service_discounted_amount = portfolio_discounted_amount * (1 - service_incentive / 100)
#                 service_incentives.append({
#                     "service_name": row["service"],
#                     "portfolio_incentive_applied": f"{portfolio_incentive}%",
#                     "service_incentive_applied": f"{service_incentive}%",
#                     "discounted_amount": round(service_discounted_amount, 2)
#                 })

#     # Step 3: Get Zone Incentive and apply it to the base amount
#     zone_incentive = get_zone_incentive(zone)  # Get the zone incentive percentage
#     zone_incentive_applied = zone_incentive
#     zone_incentive_amount = base_amount * (1 - zone_incentive / 100)  # Apply the zone incentive to the base amount

#     # Step 4: Final Amount Logic: If the discounted amount exceeds the zone incentive, use zone incentive amount as final amount
#     # If the service discounted amount is less than the zone discounted amount, apply the zone discounted amount as final amount
#     final_amount = service_discounted_amount
#     print("final1 ",  final_amount)
#     if service_discounted_amount < zone_incentive_amount:
        
#         final_amount = zone_incentive_amount
#         print("final_amount", final_amount)

#     # Return the results, correctly iterating over service_incentives
#     return [{
#         "service_name": service_incentive["service_name"],
#         "portfolio_incentive_applied": service_incentive["portfolio_incentive_applied"],
#         "service_incentive_applied": service_incentive["service_incentive_applied"],
#         "discounted_amount": service_incentive["discounted_amount"],
#         "zone_incentive_applied": f"{zone_incentive_applied}%",
#         "zone_incentive_amount": round(zone_incentive_amount, 2),
#         "final_amount": round(final_amount, 2)
#     } for service_incentive in service_incentives]  # Fixing iteration over list
