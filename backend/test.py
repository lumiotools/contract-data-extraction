from dataclasses import dataclass
import pandas as pd
from typing import Tuple
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
    origin_prefix = origin_zip[:3]
    zone_url = f"https://www.ups.com/media/us/currentrates/zone-csv/{origin_prefix}.xls"
    
    print(f"\n[1. DOWNLOADING ZONE FILE]")
    print(f"Origin ZIP prefix: {origin_prefix}")
    print(f"URL: {zone_url}")
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-GB,en;q=0.5',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }
    
    cookies = {
        'ups_language_preference': 'en_US',
        'sharedsession': '8a686f22-80cb-4e0d-9228-9e26b1396402:w',
        'HASSEENRECNOTICE': 'TRUE',
        'PIM-SESSION-ID': 'oNkI4Kve8GrUiVk1',
        'BCSessionID': 'cf430c98-6e4c-4f5f-a382-30d322853e74',
        'jedi_loc': 'eyJibG9ja2VkIjp0cnVlfQ%3D%3D',
        'JSESSIONID': '7E8164E2C0C8375C84E9B37EEFAB466A'
    }
    
    try:
        response = requests.get(
            zone_url, 
            headers=headers,
            cookies=cookies,
            allow_redirects=True
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

def get_zone_info(zone_file: str, dest_zip: str) -> int:
    dest_prefix = dest_zip[:3]
    
    print(f"\n[2. EXTRACTING ZONE INFORMATION]")
    print(f"Reading file: {zone_file}")
    print(f"Destination ZIP prefix: {dest_prefix}")
    
    try:
        # Read the zone chart Excel file
        df = pd.read_excel(zone_file, skiprows=8)
        
        print("\nZone Chart Structure:")
        print(f"Columns found: {', '.join(df.columns.tolist())}")
        print(f"Total rows: {len(df)}")
        print("\nFirst few rows of the zone chart:")
        print(df.head())
        
        # Find the zone based on destination ZIP prefix
        zone_row = df[df['Dest. ZIP'] == dest_prefix]
        
        if len(zone_row) == 0:
            print(f"✗ No zone found for destination ZIP prefix {dest_prefix}")
            return None
            
        zone = zone_row.iloc[0]['Ground']
        print(f"\n✓ Found matching row:")
        print(zone_row)
        print(f"✓ Ground Zone: {zone}")
        
        return int(zone)
        
    except Exception as e:
        print(f"✗ Error getting zone information: {str(e)}")
        return None

def download_rates_file() -> str:
    rates_url = "https://www.ups.com/assets/resources/webcontent/en_US/daily_rates.xlsx"
    
    print("\n[3. DOWNLOADING RATES FILE]")
    print(f"URL: {rates_url}")
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-GB,en;q=0.5',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(rates_url, headers=headers, allow_redirects=True)
        
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

def get_shipping_rate(rates_file: str, weight: float, zone: int, service_type: str = "UPS Ground") -> float:
    print(f"\n[4. CALCULATING SHIPPING RATE]")
    print(f"Service Type: {service_type}")
    print(f"Package Weight: {weight} lbs")
    print(f"Shipping Zone: {zone}")
    
    try:
        print(f"\nReading rates file: {rates_file}")
        # Read the daily rates Excel file
        df = pd.read_excel(rates_file, sheet_name=service_type, header=None)
        
        # Find the row with "Zones" to identify the zone columns
        zones_row = df[df[1] == "Zones"].iloc[0]
        print("\nZones row found:", zones_row.tolist())
        
        # Get the column index for our target zone
        zone_col = None
        for col in range(len(zones_row)):
            if zones_row[col] == zone:
                zone_col = col
                break
                
        if zone_col is None:
            print(f"✗ Zone {zone} not found in rate table")
            return None
            
        print(f"Zone {zone} found in column {zone_col}")
        
        # Convert weights to numeric, handling the "Lbs." text
        df[1] = df[1].astype(str).str.replace(' Lbs.', '').replace('', '0')
        df[1] = pd.to_numeric(df[1], errors='coerce')
        
        # Filter rows with valid weights
        rate_rows = df[df[1].notna() & (df[1] <= weight)].sort_values(1, ascending=False)
        
        if rate_rows.empty:
            print("✗ No valid rate found for the given weight")
            return None
            
        print("\nMatching rate row:")
        print(rate_rows.iloc[0].tolist())
        
        rate = rate_rows.iloc[0][zone_col]
        print(f"\n✓ Found Rate: ${rate:.2f}")
        return float(rate)
        
    except Exception as e:
        print(f"✗ Error getting shipping rate: {str(e)}")
        print(f"✗ Error details: {str(e)}")
        return None
    

    
def calculate_shipping(origin: Address, destination: Address, parcel: Parcel) -> Tuple[int, float]:
    print("\n[STARTING SHIPPING CALCULATION]")
    print("-" * 50)
    print("Origin Address:")
    print(f"  Street: {origin.street}")
    print(f"  City: {origin.city}")
    print(f"  State: {origin.state}")
    print(f"  ZIP: {origin.zip}")
    print(f"  Country: {origin.country}")
    
    print("\nDestination Address:")
    print(f"  Street: {destination.street}")
    print(f"  City: {destination.city}")
    print(f"  State: {destination.state}")
    print(f"  ZIP: {destination.zip}")
    print(f"  Country: {destination.country}")
    
    print("\nParcel Details:")
    print(f"  Dimensions: {parcel.length} x {parcel.width} x {parcel.height} inches")
    print(f"  Weight: {parcel.weight} lbs")
    print("-" * 50)
    
    # Download required files
    zone_file = download_zone_file(origin.zip)
    
    try:
        if zone_file:
            # Get the zone number
            zone = get_zone_info(zone_file, destination.zip)
            
            if zone is not None:
                # Download and process rates
                rates_file = download_rates_file()
                
                if rates_file:
                    # Get the shipping rate
                    rate = get_shipping_rate(rates_file, parcel.weight, zone)
                    
                    # Clean up downloaded files
                    os.remove(zone_file)
                    os.remove(rates_file)
                    
                    return zone, rate
                
    except Exception as e:
        print(f"\n✗ Error in shipping calculation: {str(e)}")
        
    finally:
        # Cleanup in case of any errors
        if 'zone_file' in locals() and os.path.exists(zone_file):
            os.remove(zone_file)
        if 'rates_file' in locals() and rates_file and os.path.exists(rates_file):
            os.remove(rates_file)
    
    return None, None

if __name__ == "__main__":
    # Create address objects
    origin = Address(
        street="465 DEVON PARK DR",
        city="WAYNE",
        state="PA",
        zip="19087",
        country="US"
    )
    
    destination = Address(
        street="350 5th Ave",
        city="New York",
        state="NY",
        zip="10118",
        country="US"
    )
    
    # Create parcel object
    parcel = Parcel(
        length=10,
        width=15,
        height=12,
        weight=100
    )
    
    # Calculate shipping
    zone, rate = calculate_shipping(origin, destination, parcel)
    
    print("\n[FINAL RESULTS]")
    print("-" * 50)
    if zone is not None and rate is not None:
        print(f"Shipping Zone: {zone}")
        print(f"Shipping Rate: ${rate:.2f}")
    else:
        print("✗ Error calculating shipping details")
    print("-" * 50)