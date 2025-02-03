from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
from pydantic import BaseModel  
from extraction_service import ContractDataExtractionService

class DiscountInput(BaseModel):
    weekly_price: float
    base_amount: float
    zone: str

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.get("/")
async def read_root():
    return JSONResponse(content={"success": True, "message": "Server is running"})


@app.post("/api/extract")
async def extract(file: UploadFile = File(...)):

    extracted_data = ContractDataExtractionService.extract(file)
    return JSONResponse(content={"success": True, "message": "Extracted data", "tables": extracted_data})






# Mock data from your previous JSON structure
portfolio_tier_incentives = [
    {"service": "UPS Next Day Air® - Letter - Prepaid\nFrtFC TP UP RS RTP", "land/zone": "ALL", "band": "0.01 - 19,429.99", "incentive": "0.00%"},
    {"service": "UPS Next Day Air® - Letter - Prepaid\nFrtFC TP UP RS RTP", "land/zone": "ALL", "band": "19,430.00 - 25,904.99", "incentive": "42.00%"}
]

service_incentives = [
    {"service": "UPS Worldwide Express® - Export - Letter - PrepaidAll", "incentive": "-53.00%"},
    {"service": "UPS Worldwide Express® - Export - Document - PrepaidAll", "incentive": "-53.00%"},
    {"service": "UPS Worldwide Express® - Export - Pak - PrepaidAll", "incentive": "-53.00%"}
]

zone_incentives = {
    "081": -68.00,
    "082": -68.00
}


# Helper function to find the portfolio tier incentive based on the weekly price
def get_portfolio_tier_incentive(weekly_price: float):
    for tier in portfolio_tier_incentives:
        # Extract the price range from the 'band' field
        band = tier["band"].split(" - ")
        lower_bound = float(band[0].replace(",", ""))  # Remove commas before converting to float
        upper_bound = float(band[1].replace(",", ""))  # Remove commas before converting to float

        if lower_bound <= weekly_price <= upper_bound:
            return float(tier["incentive"].strip('%'))  # Return the incentive as a percentage
    
    return 0  # Default incentive if no match found

# Helper function to get the service incentive for a given service name
def get_service_incentive(service_name: str):
    for service in service_incentives:
        if service["service"] == service_name:
            return abs(float(service["incentive"].strip('%')))  # Convert negative to positive
    return 0  # Default incentive if no match found

# Sample BaseModel for input
class DiscountInput(BaseModel):  # Define the model to parse and validate the input
    weekly_price: float
    base_amount: float
    zone: str

# API endpoint to calculate the discount for all services
@app.post("/calculate_discount")
async def calculate_discount(input_data: DiscountInput):
    weekly_price = input_data.weekly_price
    base_amount = input_data.base_amount
    zone = input_data.zone

    # Calculate Portfolio Tier Incentive (negated)
    portfolio_incentive = get_portfolio_tier_incentive(weekly_price)
    # Apply the negated portfolio tier incentive (treat as a positive discount)
    discounted_base_amount = base_amount * (1 + portfolio_incentive / 100)

    # Initialize results
    results = []

    # Iterate over each service and apply the discount logic
    for service in service_incentives:
        service_name = service["service"]
        
        # Step 1: Apply Service Incentive
        service_incentive = get_service_incentive(service_name)  # Now positive
        discounted_amount = discounted_base_amount * (1 - service_incentive / 100)

        # Step 2: Apply Zone Incentive (Check if calculated discount exceeds zone incentive)
        zone_incentive = abs(zone_incentives.get(zone, 0))  # Convert to positive
        total_discount = portfolio_incentive + service_incentive

        if total_discount > zone_incentive:
            final_amount = discounted_amount * (1 - zone_incentive / 100)
            zone_incentive_applied = zone_incentive
        else:
            final_amount = discounted_amount
            zone_incentive_applied = 0

        # Prepare the result for this service
        result = {
            "service_name": service_name,
            "portfolio_tier_incentive_applied": f"{portfolio_incentive}%",  # Still showing the original portfolio incentive as a percentage
            "service_incentive_applied": f"{service_incentive}%",
            "total_incentive_applied": f"{total_discount}%",
            "discounted_amount": round(discounted_amount, 2),
            "zone_incentive_applied": f"{zone_incentive_applied}%",
            "final_amount": round(final_amount, 2)
        }

        results.append(result)

    return results