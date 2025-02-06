from dataclasses import dataclass
import pandas as pd
from typing import Dict, Optional
import requests
import os

@dataclass
class Address:
    street: str
    city: str
    state: str
    zip: str
    country: str

@dataclass
class Parcel:
    length: float
    width: float
    height: float
    weight: float

def download_zone_file(origin_zip: str) -> str:
    """
    Download zone file using exact headers from successful curl request
    """
    origin_prefix = origin_zip[:3]
    zone_url = f"https://www.ups.com/media/us/currentrates/zone-csv/{origin_prefix}.xls"
    
    print(f"\nDownloading zone file for prefix {origin_prefix}")

    try:
        response = requests.get(
            zone_url, 
            headers={'User-Agent': 'PostmanRuntime/7.43.0'},
            timeout=30
        )
        
        if response.status_code == 200:
            file_name = f"zone_{origin_prefix}.xls"
            with open(file_name, 'wb') as f:
                f.write(response.content)
            print(f"✓ Successfully downloaded zone file: {file_name}")
            print(f"✓ File size: {len(response.content)} bytes")
            return file_name
        else:
            print(f"✗ Failed to download zone file. Status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Error downloading zone file: {str(e)}")
        return None

def download_rates_file() -> str:
    rates_url = "https://www.ups.com/assets/resources/webcontent/en_US/daily_rates.xlsx"
    
    print("\nDownloading rates file")
    
    try:
        response = requests.get(
            rates_url, 
            headers={'User-Agent': 'PostmanRuntime/7.43.0'},
            timeout=30
        )
        
        if response.status_code == 200:
            file_name = "daily_rates.xlsx"
            with open(file_name, 'wb') as f:
                f.write(response.content)
            print(f"✓ Successfully downloaded rates file: {file_name}")
            print(f"✓ File size: {len(response.content)} bytes")
            return file_name
        else:
            print(f"✗ Failed to download rates file. Status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Error downloading rates file: {str(e)}")
        return None

def get_service_sheet_name(service: str) -> str:
    """
    Map zone file service names to rate file sheet names
    """
    mapping = {
        'Ground': 'UPS Ground',
        '3 Day Select': 'UPS 3DA Select',
        '2nd Day Air': 'UPS 2DA',
        '2nd Day Air A.M.': 'UPS 2DA A.M.',
        'Next Day Air Saver': 'UPS NDA Saver',
        'Next Day Air': 'UPS NDA'
    }
    return mapping.get(service)

def get_all_service_rates(zone_file: str, rates_file: str, dest_zip: str, weight: float) -> Dict[str, Optional[float]]:
    """
    Get rates for all available services based on destination ZIP and weight
    """
    print(f"\n[CALCULATING RATES FOR ALL SERVICES]")
    print(f"Destination ZIP: {dest_zip}")
    print(f"Package Weight: {weight} lbs")
    
    try:
        # Read the zone file to get available services and their zones
        zone_df = pd.read_excel(zone_file, skiprows=8)
        dest_prefix = dest_zip[:3]
        
        # Remove any unnamed columns
        zone_df = zone_df[[col for col in zone_df.columns if not col.startswith('Unnamed')]]
        
        print("\nZone file columns found:")
        print(zone_df.columns.tolist())
        
        # Get the row for our destination ZIP
        zone_row = zone_df[zone_df['Dest. ZIP'] == dest_prefix]
        if zone_row.empty:
            print(f"✗ No zones found for destination ZIP prefix {dest_prefix}")
            return {}
            
        print("\nZones found for each service:")
        rates = []
        
        # Get zones for each service from all columns except 'Dest. ZIP'
        available_services = [col for col in zone_df.columns if col != 'Dest. ZIP']
        
        for service in available_services:
            zone = zone_row.iloc[0][service]
            print(f"{service}: Zone {zone}")
            
            if pd.isna(zone) or zone == '-':
                print(f"✗ {service} not available for this route")
                rates.append({
                    "serviceName": service,
                    "amount": None
                })
                continue
            
            sheet_name = get_service_sheet_name(service)
            if not sheet_name:
                print(f"✗ No rate sheet mapping found for {service}")
                rates.append({
                    "serviceName": service,
                    "amount": None
                })
                continue
                
            try:
                # Read rates file
                rate_df = pd.read_excel(rates_file, sheet_name=sheet_name, header=None)
                
                # Find the row with "Zones" to identify the zone columns
                zones_row = rate_df[rate_df[1] == "Zones"].iloc[0]
                
                # Get the column index for our zone
                zone_col = None
                zone_value = int(str(zone).split('.')[0])  # Handle decimal zones
                for col in range(len(zones_row)):
                    if zones_row[col] == zone_value:
                        zone_col = col
                        break
                
                if zone_col is None:
                    print(f"✗ Zone {zone} not found in rate table for {service}")
                    rates.append({
                        "serviceName": service,
                        "amount": None
                    })
                    continue
                
                # Convert weights to numeric, handling the "Lbs." text
                rate_df[1] = rate_df[1].astype(str).str.replace(' Lbs.', '').replace('', '0')
                rate_df[1] = pd.to_numeric(rate_df[1], errors='coerce')
                
                # Filter rows with valid weights
                rate_rows = rate_df[rate_df[1].notna() & (rate_df[1] <= weight)].sort_values(1, ascending=False)
                
                if rate_rows.empty:
                    print(f"✗ No valid rate found for {service} with weight {weight}")
                    rates.append({
                        "serviceName": service,
                        "amount": None
                    })
                    continue
                
                rate = rate_rows.iloc[0][zone_col]
                rates.append({
                    "serviceName": service,
                    "amount": float(rate)
                })
                print(f"✓ {service}: ${rate:.2f}")
                
            except Exception as e:
                print(f"✗ Error getting rate for {service}: {str(e)}")
                rates.append({
                    "serviceName": service,
                    "amount": None
                })
        
        return rates
        
    except Exception as e:
        print(f"✗ Error calculating service rates: {str(e)}")
        return {}
    

    
def calculate_shipping(origin: Address, destination: Address, parcel: Parcel) -> Dict[str, Optional[float]]:
    """
    Calculate shipping rates for all available services
    """
    print("\n[STARTING SHIPPING CALCULATION]")
    print("-" * 50)
    print("Origin Address:")
    print(f"  Street: {origin.street}")
    print(f"  City: {origin.city}")
    print(f"  State: {origin.state}")
    print(f"  ZIP: {origin.zip}")
    
    print("\nDestination Address:")
    print(f"  Street: {destination.street}")
    print(f"  City: {destination.city}")
    print(f"  State: {destination.state}")
    print(f"  ZIP: {destination.zip}")
    
    print("\nParcel Details:")
    print(f"  Dimensions: {parcel.length} x {parcel.width} x {parcel.height} inches")
    print(f"  Weight: {parcel.weight} lbs")
    print("-" * 50)
    
    # Download required files
    zone_file = download_zone_file(origin.zip)
    rates_file = download_rates_file()
    
    try:
        if zone_file and rates_file:
            # Get rates for all services
            rates = get_all_service_rates(zone_file, rates_file, destination.zip, parcel.weight)
            
            # Clean up downloaded files
            os.remove(zone_file)
            os.remove(rates_file)
            
            return rates
            
    except Exception as e:
        print(f"\n✗ Error in shipping calculation: {str(e)}")
        
    finally:
        # Cleanup in case of any errors
        if 'zone_file' in locals() and os.path.exists(zone_file):
            os.remove(zone_file)
        if 'rates_file' in locals() and rates_file and os.path.exists(rates_file):
            os.remove(rates_file)
    
    return {}

# if __name__ == "__main__":
#     # Example usage
#     origin = Address(
#         street="465 DEVON PARK DR",
#         city="WAYNE",
#         state="PA",
#         zip="19087",
#         country="US"
#     )
    
#     destination = Address(
#         street="350 5th Ave",
#         city="New York",
#         state="NY",
#         zip="10118",
#         country="US"
#     )
    
#     parcel = Parcel(
#         length=10,
#         width=15,
#         height=12,
#         weight=100
#     )
    
#     # Calculate rates for all services
#     rates = calculate_shipping(origin, destination, parcel)
    
#     print("\n[FINAL RESULTS]")
#     print("-" * 50)
#     if rates:
#         print("Available Services and Rates:")
#         for rate in rates:
#             if rate is not None:
#                 print(f"{rate["serviceName"]}: ${rate["amount"]:.2f}")
#             else:
#                 print(f"{rate["serviceName"]}: Not available")
#     else:
#         print("✗ Error calculating shipping rates")
#     print("-" * 50)