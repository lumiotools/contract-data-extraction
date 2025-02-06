import requests
import os
from pydantic import BaseModel
from ups_rates import calculate_shipping

from dotenv import load_dotenv
load_dotenv()


class Address(BaseModel):
    street: str
    city: str
    state: str
    zip: str
    country: str

class Parcel(BaseModel):
    length: float
    width: float
    height: float
    weight: float

class APIRates:
    def get_ups_rates(address_to: Address, address_from: Address, parcel: Parcel):
        rates = calculate_shipping(address_from, address_to, parcel)
        return  rates
        # headers = {
        #     "Authorization": "ShippoToken " + os.getenv("SHIPPO_API_KEY")
        # }
        # body = {
        #     "address_to": {
        #         "street1": address_to.street,
        #         "city": address_to.city,
        #         "state": address_to.state,
        #         "zip": address_to.zip,
        #         "country": address_to.country
        #     },
        #     "address_from": {
        #         "street1": address_from.street,
        #         "city": address_from.city,
        #         "state": address_from.state,
        #         "zip": address_from.zip,
        #         "country": address_from.country
        #     },
        #     "parcels": [
        #         {
        #             "length": str(parcel.length),
        #             "width": str(parcel.width),
        #             "height": str(parcel.height),
        #             "distance_unit": "in",
        #             "weight": str(parcel.weight),
        #             "mass_unit": "lb"
        #         }
        #     ],
        #     "async": False,
        #     "carrier_accounts": [
        #         os.getenv("SHIPPO_UPS_ACCOUNT_ID")
        #     ]
        # }
        # response = requests.post(
        #     "https://api.goshippo.com/shipments", headers=headers, json=body)

        # if response.status_code != 201:
        #     return []

        # data = response.json()
        # print(data)

        # if data["status"] != "SUCCESS":
        #     for message in data.get("messages", []):
        #         print(f"Error from {message['source']}: {message['text']}")
        #     return []
        
        # for rate in data["rates"]:
        #     print("\n\n")
        #     print(rate)

        # rates = [
        #     {
        #         "serviceName": rate["servicelevel"]["display_name"],
        #         "amount": rate["amount"],
        #     } for rate in data["rates"]
        # ]

        # return rates
    
    def get_fedex_rates(address_to: Address, address_from: Address, parcel: Parcel):
        auth_response = requests.post(
            "https://apis-sandbox.fedex.com/oauth/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "client_credentials",
                "client_id": os.getenv("FEDEX_API_KEY"),
                "client_secret": os.getenv("FEDEX_API_SECRET")
            }
        )

        if auth_response.status_code != 200:
            return []

        auth_data = auth_response.json()
        access_token = auth_data.get("access_token")

        if not access_token:
            return []

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token
        }
        body = {
            "accountNumber": {
            "value": os.getenv("FEDEX_ACCOUNT_NUMBER")
            },
            "requestedShipment": {
            "shipper": {
                "address": {
                "streetLines": [address_from.street],
                "city": address_from.city,
                "stateOrProvinceCode": address_from.state,
                "postalCode": address_from.zip,
                "countryCode": address_from.country
                }
            },
            "recipient": {
                "address": {
                "streetLines": [address_to.street],
                "city": address_to.city,
                "stateOrProvinceCode": address_to.state,
                "postalCode": address_to.zip,
                "countryCode": address_to.country
                }
            },
            "requestedPackageLineItems": [
                {
                "weight": {
                    "units": "LB",
                    "value": parcel.weight
                },
                "dimensions": {
                    "length": parcel.length,
                    "width": parcel.width,
                    "height": parcel.height,
                    "units": "IN"
                }
                }
            ],
            "packagingType": "YOUR_PACKAGING",
            "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
            "rateRequestType": ["LIST"]
            }
        }
        response = requests.post(
            "https://apis-sandbox.fedex.com/rate/v1/rates/quotes", headers=headers, json=body)

        if response.status_code != 200:
            return []

        data = response.json()

        if "output" not in data or "rateReplyDetails" not in data["output"]:
            return []

        rates = [
            {
                "serviceName": rate["serviceName"],
                "amount": rate["ratedShipmentDetails"][0]["totalNetCharge"],
            } for rate in data["output"]["rateReplyDetails"]
        ]

        return rates


# print(APIRates.get_ups_rates(
#     Address(street="465 DEVON PARK DR", city="WAYNE", state="PA", zip="19087", country="US"),
#     Address(street="350 5th Ave", city="New York", state="NY", zip="10118", country="US"),
#     # Address(street="Niels Bohrs Alle 23", city="Odense", state="", zip="5230", country="DK"),
#     Parcel(length=10, width=15, height=12, weight=100)
# ))
