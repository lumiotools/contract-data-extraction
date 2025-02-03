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
import difflib
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Load dummy data from JSON file


# def load_dummy_data():
#     with open("constants/dummyData.json", "r") as file:
#         return json.load(file)


# DUMMY_DATA = load_dummy_data()  # Load dummy data

# FastAPI setup
app = FastAPI()

# Allow CORS from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains (use specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

class DiscountInput(BaseModel):
    weekly_price: float
    tables_json: str


@app.get("/")
async def read_root():
    return JSONResponse(content={"success": True, "message": "Server is running"})


@app.post("/api/extract")
async def extract(file: UploadFile = File(...)):
    extracted_data = ContractDataExtractionService.extract(file)
    return JSONResponse(content={"success": True, "message": "Extracted data", "tables": extracted_data})


def find_best_match(service_name, service_list):
    """
    Finds the closest matching service name from the available list.
    Handles differences in encoding, extra words, and minor variations.
    """
    cleaned_service_name = re.sub(
        r"[^a-zA-Z0-9 ]", "", service_name).lower().strip()
    cleaned_service_list = [re.sub(
        r"[^a-zA-Z0-9 ]", "", s).lower().strip().replace("  ", " ") for s in service_list]

    matched_services = []

    for service in cleaned_service_list:
        if cleaned_service_name in service:
            matched_services.append(
                service_list[cleaned_service_list.index(service)])
    if len(matched_services) > 0:
        return matched_services

    best_match = difflib.get_close_matches(
        cleaned_service_name, cleaned_service_list, n=1, cutoff=0.6)
    return service_list[cleaned_service_list.index(best_match[0])] if best_match else None


def parse_band(band):
    """Parses the incentive band to get min and max range as floats."""
    band = band.replace(",", "")  # Remove commas
    parts = band.split(" - ")
    if len(parts) == 2:
        try:
            return float(parts[0]), float(parts[1])
        except ValueError:
            pass  # Handle in next step
    elif "and up" in band:
        try:
            return float(band.split(" ")[0]), float("inf")
        except ValueError:
            pass
    return None, None


# Helper function to get portfolio tier incentive based on weekly price
def get_portfolio_tier_incentive(table_data, weekly_price: float):
    for tier in table_data["tables"]:
        if tier["table_type"] == "portfolio_tier_incentives":
            applicable_services = []
            for entry in tier["data"]:
                min_band, max_band = parse_band(entry["band"])
                if min_band is not None and max_band is not None:
                    if min_band <= weekly_price <= max_band:
                        applicable_services.append({
                            "service": entry["service"],
                            "incentive": float(entry["incentive"].replace("%", ""))
                        })
                        # applicable_services[entry["service"]] = float(entry["incentive"].replace("%", ""))

    return applicable_services


def get_incentive_off_executive(table_data, service_name: str, weekly_price: float):
    incentives = []
    for tier in table_data["tables"]:
        if tier["table_type"] == "weight_zone_incentive" and (service_name in tier["name"] or find_best_match(service_name, [tier["name"]])):
            for row in tier["data"]:
                incentives.append(
                    abs(float(row["incentive"].replace("%", "")))
                )

        if tier["table_type"] == "zone_bands_incentive" and (service_name in tier["name"] or find_best_match(service_name, [tier["name"]])):
            for row in tier["data"]:
                min_band, max_band = parse_band(row["band"])
                if min_band is not None and max_band is not None:
                    if min_band <= weekly_price <= max_band:
                        incentives.append(
                            abs(float(row["incentive"].replace("%", "")))
                        )

        if tier["table_type"] == "zone_incentive" and (service_name in tier["name"] or find_best_match(service_name, [tier["name"]])):
            for row in tier["data"]:
                incentives.append(
                    abs(float(row["incentive"].replace("%", "")))
                )

        if tier["table_type"] == "service_incentives":
            for row in tier["data"]:
                if (service_name in row["service"] or find_best_match(service_name, [row["service"]])):
                    incentives.append(
                        abs(float(row["incentive"].replace("%", "")))
                    )

    return sum(incentives) / len(incentives) if incentives else 0


def get_maximum_possible_discount(table_data, service_name: str):
    incentives = []
    for tier in table_data["tables"]:
        if tier["table_type"] == "zone_incentive" and (service_name in tier["name"] or find_best_match(service_name, [tier["name"]])):
            for row in tier["data"]:
                incentives.append(
                    abs(float(row["incentive"].replace("%", "")))
                )

    maximum_possible_discount = max(incentives) if incentives else 100
    return maximum_possible_discount if maximum_possible_discount else 100


@app.post("/calculate_discount")
async def calculate_discount(input_data: DiscountInput):
    weekly_price = input_data.weekly_price
    tables_json = input_data.tables_json
    table_data = json.loads(tables_json)

    # Step 1: Get Service Rates (fetch from UPS API)
    ups_api = UPSApiRates()
    rates = ups_api.get_rates()

    if not rates:
        return JSONResponse(status_code=404, content={"error": "No rates found from UPS API"})

    # Print the API response for debugging
    # print("UPS API Response:", rates)

    portfolio_incentives = get_portfolio_tier_incentive(table_data, weekly_price)
    
    discounts = []

    for incentive in portfolio_incentives:
        service_name = incentive["service"]
        service_discount = incentive["incentive"]
        final_discount = service_discount

        incentive_off_executive = get_incentive_off_executive(table_data,
            service_name, weekly_price)
        final_discount = 100 - (100 - service_discount) * \
            (100 - incentive_off_executive) / 100

        service_amount = next((float(rate["amount"]) for rate in rates if find_best_match(
            rate["serviceLevel"], [service_name])), None)
        if service_amount:
            applied_discount_rate = round(service_amount * abs(final_discount) / 100, 2)

        # print("\nservice_name", service_name)
        # print("service_discount", service_discount)
        # print("incentive_off_executive", incentive_off_executive)
        # print("final_discount", final_discount)
        # print("service_amount", service_amount)
        # print("applied_discount_rate", applied_discount_rate)

        maximum_possible_discount = get_maximum_possible_discount(table_data, service_name)
        is_over_discounted = applied_discount_rate > maximum_possible_discount
        # print("maximum_possible_discount", maximum_possible_discount)
        # print("is_over_discounted", is_over_discounted)

        if service_amount:
            final_amount = applied_discount_rate if not is_over_discounted else round(
                float(service_amount) * (100 - maximum_possible_discount) / 100, 2)
            # print("final_amount", final_amount)
        else:
            final_amount = None
            
        discounts.append({
            "service_name": service_name,
            "service_discount": final_discount,
            "is_over_discounted": is_over_discounted,
            "base_amount": service_amount,
            "final_amount": final_amount
        })

    return JSONResponse(content={"success": True, "message": "Discount calculated", "data": discounts}, status_code=200)


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
