import os 
import math
import google.generativeai as genai
from google.generativeai.types.file_types import File
from dotenv import load_dotenv
import json
from fastapi import UploadFile
from google.generativeai import ChatSession
from concurrent.futures import ThreadPoolExecutor
import time
from threading import Lock
import google.api_core.exceptions

# Load environment variables and configure Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Create the model configuration
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel("gemini-2.0-flash-exp")

class FedXContractDataExtractionService:
    _lock = Lock()

    @classmethod
    def rate_limited_call(cls, func, *args, **kwargs):
        max_attempts = 3
        initial_delay = 2
        backoff_factor = 2
        last_response = None

        for attempt in range(max_attempts):
            try:
                cls._lock.acquire()
                time.sleep(1)  # Small wait after acquiring lock
                cls._lock.release()

                print(f"Calling Gemini API, attempt {attempt+1}")
                response = func(*args, **kwargs)

            except google.api_core.exceptions.ResourceExhausted as exc:
                print(f"Resource exhausted error encountered (attempt {attempt+1}): {exc}")
                time.sleep(initial_delay * (backoff_factor ** attempt))
                continue
            except Exception as exc:
                print(f"Unexpected error on attempt {attempt+1}: {exc}")
                time.sleep(initial_delay * (backoff_factor ** attempt))
                continue

            # Clean response text from markdown formatting
            cleaned_text = response.text.replace("```json\n", "").replace("\n```", "")
            try:
                data = json.loads(cleaned_text)
                # Check for valid data structure
                if data and (
                    ("tables" in data and len(data["tables"]) > 0)
                    or ("table" in data and data["table"])
                    or ("addresses" in data and data["addresses"])
                    or ("tableData" in data and data["tableData"])
                    or ("contract_type" in data and data["contract_type"])
                    or ("services" in data and data["services"])
                    or ("rows" in data and data["rows"])
                    or ("table_rows" in data)
                    or ("eligible_accounts" in data and data["eligible_accounts"])
                    or ("metadata" in data and data["metadata"])
                ):
                    return response  # Successful response
                else:
                    print(cleaned_text)
                    print(f"Received empty or incomplete data on attempt {attempt+1}, retrying...")
            except Exception as e:
                print(cleaned_text)
                print(f"Error parsing JSON response on attempt {attempt+1}: {e}")

            time.sleep(initial_delay * (backoff_factor ** attempt))
            last_response = response
        return last_response  # Return last response even if incomplete

    @classmethod
    def extract_incentive_off_effective_rates(cls, chat: ChatSession):
        """
        Extract Incentives Off Effective Rates data from FedEx contract
        """
        table = {
            "title": "Incentives off effective rate",
            "tableData": {
                "headers": ["service", "billing", "zone", "weight", "weightUnit", "discount", "tags", "destination"],
                "rows": []
            }
        }

        incentive_rates_prompt = """
        Find the Incentives Off Effective Rates tables or data from the attached contract.
        Tables will typically be found in the Express/Ground Pricing Attachment sections.
        
        Look for:
        1. Express services with discounts
        2. Ground services with discounts 
        3. Any services with percentage discounts off base rates
        
        Tables may have:
        - Service name/type
        - Zone information
        - Weight ranges 
        - Discount percentages
        - Billing types (Prepaid, Freight Collect, etc.)
        
        Extract the following for each service:
        1. Service name
        2. Billing type 
        3. Zone (zone number or 'All Zones')
        4. Weight range
        5. Discount percentage
        6. Tags (from service name)
        7. Destination (if applicable)
        
        Use this schema:
        {
            "table_rows": [
                {
                    "service": "string", #Exact service name from contract
                    "billing": "string",
                    "zone": "string", 
                    "weight": "string",
                    "weightUnit": "lbs",
                    "discount": "string", #Exact discount as written
                    "tags": ["string",...], 
                    "destination": "string or null"
                }
            ]
        }
        """

        while True:
            if len(table["tableData"]["rows"]) > 0:
                last_5_rows = table["tableData"]["rows"][-5:]
                incentive_rates_prompt += f"""
                    Continuing extraction from where we left off. Last extracted rows:
                    {str(last_5_rows)}
                """

            response = cls.rate_limited_call(chat.send_message, incentive_rates_prompt)
            data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))

            try:
                table_rows = data.get("table_rows", [])
                print("Extracted Service Discounts: ", len(table_rows))
                table["tableData"]["rows"].extend(table_rows)

                if len(table_rows) == 0:
                    break
            except:
                print("Failed to extract service discounts")

            print("Total Extracted Service Discounts: ", len(table["tableData"]["rows"]))

        # Extract metadata
        metadata_prompt = """
            Extract metadata for the incentive rates:
            1. Notes specific to different services
            2. Validity period details
            
            Specifically look for text near or below the rate tables.
            
            These are the services to find metadata for:
            {services}
            
            Use this schema:
            {
                "metadata": [
                    {
                        "service": "string",
                        "notes": ["string", ...],
                        "validityPeriod": {
                            "startDate": "string",
                            "endDate": "string"
                        }
                    }
                ]
            }
        """.replace("{services}", ", ".join(set([row["service"] for row in table["tableData"]["rows"]])))

        response = cls.rate_limited_call(chat.send_message, metadata_prompt)

        try:
            metadata = json.loads(response.text.replace("```json\n", "").replace("\n```", "")).get("metadata", [])
            print("Extracted incentive rates metadata:", metadata)
        except:
            print("Failed to extract incentive rates metadata")
            metadata = []

        table["metadata"] = metadata
        return table

    @classmethod 
    def extract_portfolio_tier_incentive_table(cls, uploadedFile: File):
        """
        Extract Portfolio Tier Incentive table data from FedEx contract 
        """
        chat = model.start_chat(history=[
            {
                'role': "user",
                'parts': [uploadedFile, "Go through the attached FedEx contract"]
            }
        ])

        portfolio_tiers_prompt = """
            Find the Portfolio Tier Incentive table(s) in the contract.
            Common locations are in the Express/Ground Pricing Attachment.
            
            Look for:
            - Service names 
            - Weekly spend bands/tiers
            - Corresponding discounts
            - Territory/zone information
            
            Find all services that have portfolio tier discounts.
            Extract all spend tiers and discounts across all pages.
            
            Use this schema:
            {
                "services": ["string",...], #All services with portfolio tiers
                "validityPeriod": {
                    "startDate": "string",
                    "endDate": "string"  
                },
                "notes": ["string",...] #Any relevant notes from contract
            }
        """

        response = cls.rate_limited_call(chat.send_message, portfolio_tiers_prompt)

        try:
            extracted_data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            services = extracted_data.get("services", [])
            validity_period = extracted_data.get("validityPeriod", {"startDate": "", "endDate": ""})
            notes = extracted_data.get("notes", [])
        except:
            print("Failed to extract portfolio tier data")
            services, validity_period, notes = [], {"startDate": "", "endDate": ""}, []

        print("Extracted Portfolio Tier services:", len(services))

        table = {
            "title": "Portfolio Tier Incentive",
            "tableData": {
                "headers": [
                    "service",
                    "land_zone", 
                    "weeklySpendMin",
                    "weeklySpendMax",
                    "currency",
                    "discount",
                    "tags"
                ],
                "rows": [],
                "notes": notes,
                "validityPeriod": validity_period
            }
        }

        # Process services in chunks
        chunk_size = 10
        for i in range(0, len(services), chunk_size):
            services_chunk = services[i:i+chunk_size]
            
            tiers_prompt = """
                Find the Portfolio Tier Incentive details for these services: {services}
                
                Extract:
                - Land/Zone info
                - Weekly spend tiers 
                - Discount percentages
                - Any service-specific tags
                
                Format spend tiers as:
                - Use "x - y" for ranges
                - Use "x and up" for open-ended tiers
                
                Use this schema:
                {
                    "table_rows": [
                        {
                            "service": "string",
                            "land_zone": "string",
                            "bandRange": "string", #"x - y" or "x and up" format
                            "currency": "string", #e.g. USD
                            "discount": "string", #percentage as written
                            "tags": ["string",...]
                        }
                    ]
                }
            """.replace("{services}", ", ".join(services_chunk))

            response = cls.rate_limited_call(chat.send_message, tiers_prompt)

            try:
                table_rows = json.loads(response.text.replace("```json\n", "").replace("\n```", "")).get("table_rows", [])
                print(f"Extracted Portfolio Tier rows for chunk {i//chunk_size + 1}:", len(table_rows))
            except:
                print(f"Failed to extract Portfolio Tier rows for chunk {i//chunk_size + 1}")
                table_rows = []

            # Process band ranges into min/max
            for row in table_rows:
                try:
                    if row["bandRange"] and "up" in row["bandRange"].lower():
                        min = row["bandRange"].lower().replace(" and up", "").replace("and up", "")
                        max = "infinity"
                    else:
                        min, max = row["bandRange"].replace("- ", "-").replace(" -","-").split("-")
                    row["weeklySpendMin"] = min
                    row["weeklySpendMax"] = max
                    del row["bandRange"]
                except:
                    print("Error processing band range:", row)
                    continue

            table["tableData"]["rows"].extend(table_rows)

        return table

    @classmethod
    def extract_minimum_net_charge_tables(cls, chat: ChatSession):
        """
        Extract Minimum Net Charge tables from FedEx contract
        """
        def process_response(response_text, part_number):
            try:
                data = json.loads(response_text.replace("```json\n", "").replace("\n```", ""))
                print(f"Data Part {part_number}")
                print(f"Extracted: {data.get('extracted_tables_count')}")
                print(f"Remaining: {data.get('remaining_tables_count')}")
                return data
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {str(e)}")
                return None

        def try_extract_batch(batch_start, max_retries=3):
            for attempt in range(1, max_retries + 1):
                prompt = f"""
                Extract minimum net charge tables in batches of up to 10 tables per batch.
                Starting from table #{batch_start + 1}.
                
                Look for:
                - Service name/type
                - Zone codes
                - Adjustment values
                
                Key requirements:
                1. Keep tables complete - don't split across batches
                2. Handle tables spanning multiple pages 
                3. Count remaining tables after this batch
                
                Format adjustment values as exact numeric percentage strings.
                Use null for non-numeric values.
                Include exact zone codes as shown.
                
                Use this schema:
                {{
                    "tables": [
                        {{
                            "table_type": "zone_incentive_min_charge",
                            "name": "string",
                            "data": [
                                {{
                                    "zone": "string",
                                    "incentive": "string or null"
                                }}
                            ]
                        }}
                    ],
                    "extracted_tables_count": int,
                    "remaining_tables_count": int,
                    "notes": "string",
                    "validityPeriod": {{
                        "startDate": "string",
                        "endDate": "string"
                    }}
                }}
                """

                response = cls.rate_limited_call(chat.send_message, prompt)

                if not response.text.strip():
                    print(f"Empty response on attempt {attempt}, retrying...")
                    continue

                try:
                    data = process_response(response.text, batch_start)
                    if data and data.get("tables"):
                        return data
                except Exception as e:
                    print(f"Error processing response: {str(e)}")

            return None

        def extract_billing_type(service_name):
            if "Prepaid" in service_name:
                return "Prepaid"
            elif "Freight Collect" in service_name:
                return "Freight Collect"
            else:
                return "Unknown"

        def format_combined_table(tables, notes, validity_period):
            return {
                "title": "Minimum Net Charge",
                "tableData": {
                    "headers": ["service", "billing", "zone", "adjustmentDiscount", "tags"],
                    "rows": [
                        {
                            "service": " ".join([w for w in t["name"].split()[:3] if w.lower() != "to"]),
                            "billing": extract_billing_type(t["name"]),
                            "zone": row["zone"],
                            "adjustmentDiscount": row["incentive"],
                            "tags": [tag for tag in t["name"].split()[3:] if tag != "-"]
                        }
                        for t in tables
                        for row in t["data"]
                    ],
                    "notes": notes,
                    "validityPeriod": validity_period
                }
            }

        # Start collecting tables
        all_tables = []
        batch_start = 0
        notes = []
        validity_period = {}

        while True:
            batch_data = try_extract_batch(batch_start)
            if not batch_data:
                break

            tables = batch_data.get("tables", [])
            remaining = batch_data.get("remaining_tables_count", 0)
            extracted = batch_data.get("extracted_tables_count", 0)

            if not tables:
                break

            all_tables.extend(tables)
            notes.append(batch_data.get("notes", ""))
            validity_period.update(batch_data.get("validityPeriod", {}))

            print(f"\nBatch progress:")
            print(f"- Tables in batch: {len(tables)}")
            print(f"- Total tables: {len(all_tables)}")
            print(f"- Tables remaining: {remaining}")

            if remaining == 0:
                break

            batch_start += len(tables)

        print(f"\nExtraction completed. Total tables: {len(all_tables)}")
        
        return format_combined_table(all_tables, notes, validity_period)

    @classmethod
    def extract_service_adjustment_table(cls, chat: ChatSession):
        """
        Extract Service Adjustment table data from FedEx contract
        """
        service_adjustment_prompt = """
            Find service adjustment tables in the Express/Ground Pricing sections.
            These tables typically show base service rates and adjustments.
            
            Look for tables with:
            1. Service name
            2. Minimum charge type
            3. Zone information  
            4. Base rate
            5. Adjustment value
            
            Also extract:
            - Currency for adjustments
            - Tags/categories for services
            - Contract validity period
            - Any relevant notes
            
            Use this schema:
            {
                "title": "Service Adjustment",
                "tableData": {
                    "headers": [
                        "service",
                        "minimumPer",
                        "zone", 
                        "baseRate",
                        "adjustment",
                        "currency",
                        "tags"
                    ],
                    "rows": [
                        {
                            "service": "string",
                            "minimumPer": "string",
                            "zone": "string",
                            "baseRate": "string",
                            "adjustment": "string or null",
                            "currency": "string",
                            "tags": ["string",...]
                        }
                    ],
                    "notes": ["string",...],
                    "validityPeriod": {
                        "startDate": "string",
                        "endDate": "string"
                    }
                }
            }
        """
        
        response = cls.rate_limited_call(chat.send_message, service_adjustment_prompt)

        try:
            extracted_data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            return extracted_data
        except:
            print("Failed to extract service adjustment data")
            return []

    @classmethod
    def extract_electronic_pld_bonus_table(cls, chat: ChatSession):
        """
        Extract Electronic PLD Bonus table data from FedEx contract
        """
        electronic_pld_prompt = """
        Your task is to analyze this FedEx contract for Electronic PLD Bonus information.
        
        If you find any Electronic PLD Bonus data, return it in this exact JSON format:
        {
            "title": "Electronic PLD Bonus",
            "found": true,
            "tableData": {
                "headers": ["service", "bonus", "tags"],
                "rows": [
                    {
                        "service": "string",
                        "bonus": "string or null",
                        "tags": ["string"]
                    }
                ],
                "notes": ["string"],
                "validityPeriod": {
                    "startDate": "string",
                    "endDate": "string"
                }
            }
        }

        If you DO NOT find any Electronic PLD Bonus information, return exactly this JSON:
        {
            "title": "Electronic PLD Bonus",
            "found": false,
            "message": "No Electronic PLD Bonus information found in the document"
        }

        You must return only valid JSON, with no other text before or after.
        """

        response = cls.rate_limited_call(chat.send_message, electronic_pld_prompt)

        try:
            # Clean up the response to get just the JSON
            json_text = response.text
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0]
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0]
                
            extracted_data = json.loads(json_text.strip())
            return extracted_data
        except Exception as e:
            print(f"Failed to extract Electronic PLD Bonus data: {str(e)}")
            return {
                "title": "Electronic PLD Bonus",
                "found": false,
                "message": "Error processing response"
            }



    @classmethod
    def extract_contract_details(cls, chat: ChatSession):
        """
        Extract basic contract details and eligible accounts
        """
        contract_details_prompt = """
            Extract the following contract information:
            
            1. Account numbers and details from "Account Numbers" section
            2. Identify carrier (FedEx)
            3. Format addresses with complete company name, street, city, state/zip
            4. Extract any commodity tier information
            
            Use this schema:
            {
                "carrier": "string",
                "eligible_accounts": [
                    {
                        "account_number": "string",
                        "name": "string", 
                        "address": "string",
                        "zip": "string",
                        "commodity_tier": "string"
                    }
                ]
            }
        """

        response = cls.rate_limited_call(chat.send_message, contract_details_prompt)

        try:
            data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            return data
        except:
            print("Failed to extract contract details")
            return None

    @classmethod
    def fedx_extract(cls, contract: UploadFile):
        """
        Main extraction method that coordinates all data extraction
        """
        # Upload contract to Gemini
        uploaded_file = genai.upload_file(contract.file, mime_type=contract.content_type)
        print("Uploaded file:", uploaded_file.name)

        # Initialize chat session
        chat = model.start_chat(history=[
            {
                'role': "user",
                'parts': [uploaded_file, "Go through the attached contract"]
            }
        ])

        # Execute extractions concurrently
        with ThreadPoolExecutor() as executor:
            incentives_future = executor.submit(cls.extract_incentive_off_effective_rates, chat)
            portfolio_tiers_future = executor.submit(cls.extract_portfolio_tier_incentive_table, uploaded_file)  
            min_charges_future = executor.submit(cls.extract_minimum_net_charge_tables, chat)
            service_adjustments_future = executor.submit(cls.extract_service_adjustment_table, chat)
            electronic_pld_future = executor.submit(cls.extract_electronic_pld_bonus_table, chat)
            contract_details_future = executor.submit(cls.extract_contract_details, chat)

            # Gather results
            tables = []
            tables.append(incentives_future.result())
            tables.append(portfolio_tiers_future.result())
            tables.append(min_charges_future.result()) 
            tables.append(service_adjustments_future.result())
            tables.append(electronic_pld_future.result())

            details = contract_details_future.result()

        return {
            "details": details,
            "tables": tables
        }