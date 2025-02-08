from dataclasses import dataclass
import pandas as pd
from typing import Dict, Optional
import requests
import os
from pathlib import Path
import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Suppress SSL warnings

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

def ensure_constants_dir():
    """Ensure the constants directory exists"""
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    constants_dir = current_dir / 'constants'
    constants_dir.mkdir(exist_ok=True)
    return constants_dir

def download_zone_file(origin_zip: str) -> tuple[str, bool]:
    """Download zone file with proper path handling and fallback"""
    constants_dir = ensure_constants_dir()
    fallback_files = [
        constants_dir / 'fallback_190.xls',
        constants_dir / '190.xls'
    ]
    
    origin_prefix = origin_zip[:3]
    urls = [
        f"https://www.ups.com/media/us/currentrates/zone-csv/{origin_prefix}.xls"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cookie": "",
    }

    for url in urls:
        print(f"\nAttempting to download zone file from: {url}")
        try:
            session = requests.Session()
            retries = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
            session.mount('https://', HTTPAdapter(max_retries=0))
            
            response = session.get(
                url,
                headers=headers,
                timeout=15,
                verify=False
            )
            
            if response.status_code == 200 and len(response.content) > 0:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = constants_dir / f"zone_{origin_prefix}_{timestamp}.xls"
                
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                print(f"✓ Successfully downloaded zone file: {file_name}")
                return str(file_name), True
            else:
                print(f"✗ Download failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            continue

    for fallback_file in fallback_files:
        if fallback_file.exists():
            print(f"Using fallback file: {fallback_file}")
            return str(fallback_file), False
            
    print("❌ No fallback files found!")
    return str(fallback_files[0]), False

def download_rates_file() -> tuple[str, bool]:
    """Download rates file with proper path handling and fallback"""
    constants_dir = ensure_constants_dir()
    fallback_files = [
        constants_dir / 'fallback_daily_rates.xlsx',
        constants_dir / 'daily_rates.xlsx'
    ]
    
    url = "https://www.ups.com/assets/resources/webcontent/en_US/daily_rates.xlsx"
    
    print("\nAttempting to download rates file")
    print(f"URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cookie": "",
    }
    
    try:
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        response = session.get(
            url,
            headers=headers,
            timeout=15,
            verify=False
        )
        
        if response.status_code == 200 and len(response.content) > 0:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = constants_dir / f"daily_rates_{timestamp}.xlsx"
            
            with open(file_name, 'wb') as f:
                f.write(response.content)
            print(f"✓ Successfully downloaded rates file: {file_name}")
            return str(file_name), True
        else:
            print(f"✗ Failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    for fallback_file in fallback_files:
        if fallback_file.exists():
            print(f"Using fallback file: {fallback_file}")
            return str(fallback_file), False
            
    print("❌ No fallback files found!")
    return str(fallback_files[0]), False

def get_service_sheet_name(service: str) -> str:
    """Map zone file service names to rate file sheet names"""
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
    """Get rates for all available services based on destination ZIP and weight"""
    print(f"\n[CALCULATING RATES FOR ALL SERVICES]")
    print(f"Destination ZIP: {dest_zip}")
    print(f"Package Weight: {weight} lbs")
    
    try:
        zone_df = pd.read_excel(zone_file, skiprows=8)
        dest_prefix = dest_zip[:3]
        
        zone_df = zone_df[[col for col in zone_df.columns if not col.startswith('Unnamed')]]
        
        print("\nZone file columns found:")
        print(zone_df.columns.tolist())
        
        zone_row = zone_df[zone_df['Dest. ZIP'] == dest_prefix]
        if zone_row.empty:
            print(f"✗ No zones found for destination ZIP prefix {dest_prefix}")
            return {}
            
        print("\nZones found for each service:")
        rates = []
        
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
                rate_df = pd.read_excel(rates_file, sheet_name=sheet_name, header=None)
                zones_row = rate_df[rate_df[1] == "Zones"].iloc[0]
                
                zone_col = None
                zone_value = int(str(zone).split('.')[0])
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
                
                rate_df[1] = rate_df[1].astype(str).str.replace(' Lbs.', '').replace('', '0')
                rate_df[1] = pd.to_numeric(rate_df[1], errors='coerce')
                
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
    """Calculate shipping rates for all available services"""
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
    zone_file, zone_is_downloaded = download_zone_file(origin.zip)
    rates_file, rates_is_downloaded = download_rates_file()
    
    downloaded_files = []
    if zone_is_downloaded:
        downloaded_files.append(zone_file)
    if rates_is_downloaded:
        downloaded_files.append(rates_file)
    
    try:
        if zone_file and rates_file:
            # Get rates for all services
            rates = get_all_service_rates(zone_file, rates_file, destination.zip, parcel.weight)
            return rates
            
    except Exception as e:
        print(f"\n✗ Error in shipping calculation: {str(e)}")
        return {}
        
    finally:
        # Only cleanup downloaded files, not fallback files
        for file in downloaded_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"Cleaned up downloaded file: {file}")
                except Exception as e:
                    print(f"Error cleaning up file {file}: {str(e)}")
    
    return {}

# Example usage:
# if __name__ == "__main__":
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
#             if rate["amount"] is not None:
#                 print(f"{rate['serviceName']}: ${rate['amount']:.2f}")
#             else:
#                 print(f"{rate['serviceName']}: Not available")
#     else:
#         print("✗ Error calculating shipping rates")
#     print("-" * 50)