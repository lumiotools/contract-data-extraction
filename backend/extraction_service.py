import os
import google.generativeai as genai
from google.generativeai.types.file_types import File
from dotenv import load_dotenv
import json
from fastapi import UploadFile
from google.generativeai import ChatSession
from concurrent.futures import ThreadPoolExecutor
import time
from threading import Lock
import google.api_core.exceptions  # To catch ResourceExhausted errors

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


class ContractDataExtractionService:
    _lock = Lock()

    @classmethod
    def rate_limited_call(cls, func, *args, **kwargs):
        max_attempts = 5
        initial_delay = 2
        backoff_factor = 2
        last_response = None
        for attempt in range(max_attempts):
            try:
                cls._lock.acquire()
                time.sleep(1)  # small wait after acquiring lock
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

            # Clean the response text from markdown formatting.
            cleaned_text = response.text.replace("```json\n", "").replace("\n```", "")
            try:
                data = json.loads(cleaned_text)
                # Check for expected keys and non-empty data
                if data and (
                    ("tables" in data and len(data["tables"]) > 0)
                    or ("table" in data and data["table"])
                    or ("addresses" in data and data["addresses"])
                    or ("contract_type" in data and data["contract_type"])
                ):
                    return response  # Successful response
                else:
                    print(f"Received empty or incomplete data on attempt {attempt+1}, retrying...")
            except Exception as e:
                print(f"Error parsing JSON response on attempt {attempt+1}: {e}")

            time.sleep(initial_delay * (backoff_factor ** attempt))
            last_response = response
        return last_response  # Return the last response even if it is incomplete

    @classmethod
    def extract_weight_destination_zone_bands_incentives(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract all the tables in the attached contract in JSON format which match the following conditions:
              1. Table has 'Weight (lbs)', 'Zones', and 'Discount' columns. (Table Type: `weight_zone_incentive`)
              2. Table has 'Zones', 'Bands ($)', and 'Discount' columns. (Table Type: `zone_bands_incentive`)
              3. Table has 'Zones' and 'Discount' columns. (Table Type: `zone_incentive`)
              4. Table has 'Destination', 'Zone', and 'Discount' columns. (Table Type: `destination_zone_incentive`)
              5. Table has 'Destination', 'Zone', 'Weight', and 'Discount' columns. (Table Type: `destination_zone_weight_incentive`)
            
            **# Updated Prompt:**
            For every table row, ensure that the "incentive" value is provided strictly as a numeric percentage string (for example, "18.00%"). 
            If a numeric discount is not available, return null for that field.
            
            Data not shown in a clear tabular format should be ignored.
            Do not merge separate tables or split a table.
            Process tables in the order they appear.
            
            Start with the first 4 tables.
            Extract exactly 4 tables.
            
            Use the following output schema:
            {
                "tables": [
                  {
                    "table_type": "string", 
                    "name": "string",           
                    "data": [
                      { 
                        "destination": "string or null",
                        "weight": "string",
                        "zone": "string",
                        "band": "string",
                        "incentive": "percentage (numeric string, or null)"
                      }
                    ]
                  }
                ]
            }
            
            Exclude tables for:
              - Portfolio Tier Incentives
              - Zone Adjustment
              - Additional Handling Charge
              - Electronic PLD Bonus
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        try:
            data_part1 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        except:
            return []
        print("Data Part 1", len(data_part1.get("tables", [])))
        
        response = cls.rate_limited_call(chat.send_message, """
            Extract all the tables in the attached contract in JSON format which match the following conditions:
              1. Table has 'Weight (lbs)', 'Zones', and 'Discount' columns. (Table Type: `weight_zone_incentive`)
              2. Table has 'Zones', 'Bands ($)', and 'Discount' columns. (Table Type: `zone_bands_incentive`)
              3. Table has 'Zones' and 'Discount' columns. (Table Type: `zone_incentive`)
              4. Table has 'Destination', 'Zone', and 'Discount' columns. (Table Type: `destination_zone_incentive`)
              5. Table has 'Destination', 'Zone', 'Weight', and 'Discount' columns. (Table Type: `destination_zone_weight_incentive`)
            
            **# Updated Prompt:**
            For each row, ensure the "incentive" field is strictly a numeric percentage (e.g. "18.00%"). 
            If the incentive is not a valid numeric percentage, output null.
            
            Do not merge or split tables.
            Process tables in contract order.
            
            Start with the 6th table (UPS World wide Express® - Export - Pak - Prepaid All - Incentives Off Effective Rates)
            and end with the table titled "UPS World wide Expedited® - Export - Package - Prepaid All".
            
            Use the following output schema:
            {
                "tables": [
                  {
                    "table_type": "string",
                    "name": "string",
                    "data": [
                      { 
                        "destination": "string or null",
                        "weight": "string",
                        "zone": "string",
                        "band": "string",
                        "incentive": "percentage (numeric string, or null)"
                      }
                    ]
                  }
                ]
            }
            
            Exclude:
              - Tables with only a title (no tabular data)
              - Portfolio Tier Incentives
              - Zone Adjustment
              - Additional Handling Charge
              - Electronic PLD Bonus
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        try:
            data_part2 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        except:
            return data_part1.get("tables", [])
        print("Data Part 2", len(data_part2.get("tables", [])))
        
        tables = []
        tables.extend(data_part1.get("tables", []))
        tables.extend(data_part2.get("tables", []))
        return tables

    @classmethod
    def extract_service_incentive_tables(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract all the incentives mentioned in textual form (non-tabular) from the attached contract in JSON format.
            
            **# Updated Prompt:**
            For the discount values, output only a numeric percentage string (e.g. "18.00%"). 
            If a discount is not provided as a numeric percentage, output null.
            
            Use the following output schema:
            {
              "table": 
                {
                  "table_type": "service_incentives",
                  "name": "Service Incentives",
                  "data": [
                    { 
                        "service": "string",
                        "incentive": "percentage (numeric string, or null)"
                    }
                  ]
                }
            }
            
            Do not include any rows that lack a discount value.
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        try:
            data_part1 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        except:
            return []
        print("Data Part 3")
        return [data_part1.get("table", {})]

    @classmethod
    def extract_portfolio_tier_incentives_table(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract the Portfolio Tier Incentive Table from the attached contract in JSON format.
            
            Extract all available service(s) for the first 2 bands (eg: "0.01 - 19,429.99" and "19,430.00 - 25,904.99").
            
            For each row, ensure the "incentive" value is returned as a numeric percentage string (e.g. "18.00%","0.00%"). 
            If the discount is not numeric, output null.
            
            Use the following output schema:
            {
                "table": {
                  "table_type": "portfolio_tier_incentives",
                  "name": "string",
                  "data": [
                    {
                      "service": "string",
                      "land/zone": "string",
                      "band": "string",
                      "incentive": "percentage (numeric string, or null)"
                    }
                  ]
                }
            }
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 4")
        try:
            data_part1 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        except:
            return []
        table = data_part1.get("table", {})
        print("First part row count:", len(table.get("data", [])))
        
        response = cls.rate_limited_call(chat.send_message, """
            Extract the Portfolio Tier Incentive Table from the attached contract in JSON format.
            
            Extract all available service(s) for the next 2 bands ("25,905.00 - 37,779.99" and "37,780.00 - 43,174.99").            

            For each row, return the "incentive" as a numeric percentage string (e.g. "18.00%"). 
            If not numeric, output null.
            
            Use the following output schema:
            {
                "table": {
                  "table_type": "portfolio_tier_incentives",
                  "name": "string",
                  "data": [
                    {
                      "service": "string",
                      "land/zone": "string",
                      "band": "string",
                      "incentive": "percentage (numeric string, or null)"
                    }
                  ]
                }
            }
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 5")
        try:
            data_part2 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        except:
            return [table]
        print("Second part row count:", len(data_part2.get("table", {}).get("data", [])))
        table.setdefault("data", []).extend(data_part2.get("table", {}).get("data", []))
        
        response = cls.rate_limited_call(chat.send_message, """
            Extract the Portfolio Tier Incentive Table from the attached contract in JSON format.
            
            Extract all available service(s) for the final 2 bands ("43,175.00 - 48,569.99" and "48,570.00 and up").
            
            For each row, return the "incentive" strictly as a numeric percentage string (e.g. "18.00%"). 
            If the value is non-numeric, output null.
            
            Use the following output schema:
            {
                "table": {
                  "table_type": "portfolio_tier_incentives",
                  "name": "string",
                  "data": [
                    {
                      "service": "string",
                      "land/zone": "string",
                      "band": "string",
                      "incentive": "percentage (numeric string, or null)"
                    }
                  ]
                }
            }
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 6")
        try:
            data_part3 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        except:
            return [table]
        print("Third part row count:", len(data_part3.get("table", {}).get("data", [])))
        table.setdefault("data", []).extend(data_part3.get("table", {}).get("data", []))
        return [table]

    @classmethod
    def extract_zone_incentives_tables(cls, chat: ChatSession):
        def process_response(response_text, part_number):
            print(response_text)
            try:
                data = json.loads(response_text.replace("```json\n", "").replace("\n```", ""))
                print(f"Data Part {part_number}")
                print(f"Extracted:", data.get("extracted_tables_count"))
                print(f"Remaining:", data.get("remaining_tables_count"))
                return data
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {str(e)}")
                return None

        def try_extract_batch(batch_start, max_retries=3):
            for attempt in range(1, max_retries + 1):
                prompt = f"""
                You are processing zone adjustment incentive tables in batches.
                Each batch should contain UP TO 10 COMPLETE TABLES. Try to fill each batch with 10 tables unless fewer remain.

                Starting from table #{batch_start + 1}, extract the next batch of zone adjustment incentive tables from the contract.
                These tables have:
                - Service name as the header/name
                - Zone codes (e.g. "081", "082", "083", etc.)
                - Incentive adjustment percentages

                Important batch processing rules:
                1. Process exactly 10 tables if 10 or more tables remain
                2. Process all remaining tables if fewer than 10 remain
                3. Keep tables complete - don't split tables across batches
                4. Count remaining tables AFTER this batch

                Output requirements:
                - Format incentive values as exact numeric percentage strings (e.g. "-65.00%")
                - Use null for non-numeric incentive values
                - Include exact zone codes as shown
                - Provide accurate extracted_tables_count and remaining_tables_count
                
                Use this exact schema:
                {{
                    "tables": [
                      {{
                        "table_type": "zone_incentive_min_charge",
                        "name": "string",
                        "data": [
                          {{
                            "zone": "string",
                            "incentive": "percentage (numeric string, or null)"
                          }}
                        ]
                      }}
                    ],
                    "extracted_tables_count": int,  // Number of tables in THIS batch
                    "remaining_tables_count": int   // Number of tables remaining AFTER this batch
                }}
                """
                
                print(f"Calling Gemini API, attempt {attempt}")
                response = cls.rate_limited_call(chat.send_message, prompt)
                
                if not response.text.strip():
                    print(f"Received empty or incomplete data on attempt {attempt}, retrying...")
                    continue
                    
                try:
                    data = process_response(response.text, batch_start)
                    if data and data.get("tables"):
                        return data
                except Exception as e:
                    print(f"Error processing response on attempt {attempt}: {str(e)}")
                    
            return None

        # Start collecting all tables
        all_tables = []
        batch_start = 0
        
        while True:
            batch_data = try_extract_batch(batch_start)
            if not batch_data:
                break
                
            current_tables = batch_data.get("tables", [])
            remaining_count = batch_data.get("remaining_tables_count", 0)
            extracted_count = batch_data.get("extracted_tables_count", 0)
            
            if not current_tables:
                break
                
            all_tables.extend(current_tables)
            print(f"\nBatch progress:")
            print(f"- Tables in this batch: {len(current_tables)}")
            print(f"- Total tables so far: {len(all_tables)}")
            print(f"- Tables remaining: {remaining_count}")
            
            if remaining_count == 0:
                break
                
            batch_start += len(current_tables)
            
        print(f"\nExtraction completed. Total tables extracted: {len(all_tables)}")
        return all_tables
    
    
    @classmethod
    def extract_service_min_per_zone_base_rate_adjustment_table(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract the table in the attached contract in JSON format that contains all of the following headers:
              1. 'Service'
              2. 'Minimum Per'
              3. 'Zone'
              4. 'Base Rate'
              5. 'Adjustment'
            
            Target only tabular data.
            Skip any table that is missing a header.
            
            There are 2 such tables; extract both.
            
            **# Updated Prompt:**
            For the 'adjustment' field, ensure that it is returned as a numeric string (optionally with a leading minus sign) or null if not available.
            
            Use the following output schema:
            {
                "table": {
                  "table_type": "service_min_per_zone_base_rate_adjustment",
                  "name": "Minimum Net Charge",
                  "data": [
                    {
                      "service": "string",
                      "min_per": "string",
                      "zone": "string",
                      "base_rate": "string",
                      "adjustment": "string (numeric, or null)"
                    }
                  ]
                }
            }
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 9")
        try:
            data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            return [data.get("table", {})]
        except:
            return []

    @classmethod
    def extract_additional_handling_charge_table(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract the table in the attached contract in JSON format that has the headers 'Service(s)', 'Land/Zone', and 'Incentives', 
            with the title 'Additional Handling Charge ($)'.
            
            **# Updated Prompt:**
            For the 'incentives' field, return only a numeric percentage string (e.g. "18.00%") or null if not applicable.
            
            Use the following output schema:
            {
                "table": {
                  "table_type": "additional_handling_charge",
                  "name": "string",
                  "data": [
                    {
                      "service": "string",
                      "land/zone": "string",
                      "incentives": "percentage (numeric string, or null)"
                    }
                  ]
                }
            }
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 10")
        try:
            data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            return [data.get("table", {})]
        except:
            return []

    @classmethod
    def extract_electronic_pld_bonus_table(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract the table in the attached contract in JSON format that has the headers 'Service(s)' and 'Electronic PLD Bonus'.
            
            **# Updated Prompt:**
            Ensure that the 'electronic_pld_bonus' field is returned as a numeric percentage string (e.g. "18.00%") or null.
            
            Use the following output schema:
            {
                "table": {
                  "table_type": "electronic_pld_bonus",
                  "name": "string",
                  "data": [
                    {
                      "service": "string",
                      "electronic_pld_bonus": "percentage (numeric string, or null)"
                    }
                  ]
                }
            }
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 11")
        try:
            data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            return [data.get("table", {})]
        except:
            return []

    @classmethod
    def extract_address(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract ALL the addresses from the Account Numbers section of the contract in JSON format.
            Format each address as a complete object (with street number, street, city, stateCode, zipCode, and countryCode).
            
            Use the following output schema:
            {
                "addresses": [
                    {
                        "name": "string",
                        "street": "string",
                        "city": "string",
                        "stateCode": "string",
                        "zipCode": "string",
                        "countryCode": "US"
                    }
                ]
            }
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        try:
            data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            addresses = data.get("addresses", [])
            return addresses[0] if addresses else None
        except:
            return None

    @classmethod
    def extract_contract_type(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Determine if this is a UPS or FedEx contract based on the content of the attached document.
            Return only "ups" or "fedex" in lowercase.
            
            Use the following output schema:
            {
                "contract_type": "string"
            }
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        try:
            data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            return data.get("contract_type", None)
        except:
            return None

    @classmethod
    def extract(cls, contract: UploadFile):
        # Upload the file to Gemini
        uploadedFile = genai.upload_file(contract.file, mime_type=contract.content_type)
        print("Uploaded file:", uploadedFile.name)
        
        # Start a chat session with the uploaded file in the history
        chat = model.start_chat(history=[
            {
                'role': "user",
                'parts': [uploadedFile, "Go through the attached contract and answer my questions."]
            }
        ])
        
        # Execute all extractions concurrently
        with ThreadPoolExecutor() as executor:
            extracted_weight_zone_incentives_tables_future = executor.submit(cls.extract_weight_destination_zone_bands_incentives, chat)
            extracted_service_incentive_tables_future = executor.submit(cls.extract_service_incentive_tables, chat)
            extracted_portfolio_tier_incentives_tables_future = executor.submit(cls.extract_portfolio_tier_incentives_table, chat)
            extracted_zone_incentives_tables_future = executor.submit(cls.extract_zone_incentives_tables, chat)
            extracted_service_min_per_zone_base_rate_adjustment_table_future = executor.submit(cls.extract_service_min_per_zone_base_rate_adjustment_table, chat)
            extracted_additional_handling_charge_table_future = executor.submit(cls.extract_additional_handling_charge_table, chat)
            extracted_electronic_pld_bonus_table_future = executor.submit(cls.extract_electronic_pld_bonus_table, chat)
            
            extracted_weight_zone_incentives_tables = extracted_weight_zone_incentives_tables_future.result()
            extracted_service_incentive_tables = extracted_service_incentive_tables_future.result()
            extracted_portfolio_tier_incentives_tables = extracted_portfolio_tier_incentives_tables_future.result()
            extracted_zone_incentives_tables = extracted_zone_incentives_tables_future.result()
            extracted_service_min_per_zone_base_rate_adjustment_table = extracted_service_min_per_zone_base_rate_adjustment_table_future.result()
            extracted_additional_handling_charge_table = extracted_additional_handling_charge_table_future.result()
            extracted_electronic_pld_bonus_table = extracted_electronic_pld_bonus_table_future.result()
        
        with ThreadPoolExecutor() as executor:
            extracted_address_future = executor.submit(cls.extract_address, chat)
            extracted_contract_type_future = executor.submit(cls.extract_contract_type, chat)
            
            extracted_address = extracted_address_future.result()
            extracted_contract_type = extracted_contract_type_future.result()
        
        tables = []
        tables.extend(extracted_weight_zone_incentives_tables)
        tables.extend(extracted_service_incentive_tables)
        tables.extend(extracted_portfolio_tier_incentives_tables)
        tables.extend(extracted_zone_incentives_tables)
        tables.extend(extracted_service_min_per_zone_base_rate_adjustment_table)
        tables.extend(extracted_additional_handling_charge_table)
        tables.extend(extracted_electronic_pld_bonus_table)
        
        print("Extracted Address:", extracted_address)
        return {
            "tables": tables,
            "address": extracted_address,
            "contract_type": extracted_contract_type
        }
