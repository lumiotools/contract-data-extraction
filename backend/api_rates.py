import requests
import os
from dotenv import load_dotenv
load_dotenv()

class UPSApiRates:
    def get_rates(self):
        headers = {
            "Authorization": "ShippoToken " + os.getenv("SHIPPO_API_KEY")
        }
        body = {
            "address_to": {
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "US"
            },
            "address_from": {
                "name": " WALLQUEST",
                "street1": "465 DEVON PARK DR",
                "city": "WAYNE",
                "state": "PA",
                "zip": "19087",
                "country": "US"
            },
            "parcels": [
                {
                    "length": "10",
                    "width": "15",
                    "height": "12",
                    "distance_unit": "in",
                    "weight": "100",
                    "mass_unit": "lb"
                }
            ],
            "async": False,
            "carrier_accounts": [
                "97254c52f74049c3aaa85b4fda96e005"
            ]
        }
        response = requests.post("https://api.goshippo.com/shipments", headers=headers, json=body)
        
        if response.status_code != 201:
            return []
        
        data = response.json()
        
        if data["status"] != "SUCCESS":
            return []
        
        rates = [
            {
                "serviceLevel": rate["servicelevel"]["display_name"],
                "amount": rate["amount"],
            } for rate in data["rates"]
        ]
        
        return rates
        
print(UPSApiRates().get_rates())