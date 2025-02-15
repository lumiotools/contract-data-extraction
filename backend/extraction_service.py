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
                    or ("services" in data and data["services"])
                    or ("table_rows" in data)
                    or ("rows" in data and data["rows"])
                    or ("eligible_accounts" in data and data["eligible_accounts"])
                    or ("tableData" in data and data["tableData"])
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
        return last_response  # Return the last response even if it is incomplete

    
    @classmethod
    def extract_incentive_off_effective_rates(cls, chat: ChatSession):
        table = {
            "title": "Incentives off effective rate",
            "tableData": {
                "headers": ["service", "billing", "zone", "weight", "weightUnit", "discount", "tags", "destination"],
                "rows": []
            }
        }
        incentive_off_effective_rates_extraction_prompt = """
                Find the Incentives Off Effective Rates tables or data from the attached contract.
                It will be in the tabular form or single line format.
                Each one will have a Service Name.
                For Tabular Format the service Name will be on the top of the table.
                For Single Line Format the service Name will be at the start of the line.
                
                Table Selection Criteria: All tables and data above Portfolio Tier Incentives table.
                
                The Tables can be of any combination of the following columns:
                - Service Name
                - Weight Range
                - Zone
                - Discount Percentage
                - Destination
                
                Extract the Following Information:
                1. Service Name (Extracted from the table or line)
                2. Billing Type (Prepaid, Freight Collect, etc.)
                3. Zone (Zone Number or ALL)
                4. Weight Range (Weight in lbs)
                5. Discount (Percentage)
                6. Tags (Extracted from the Service Name)
                7. Destination (If available)                
                
                **Note:** Tables to Ignore:
                - Portfolio Tier Incentives 
                - Additional Handling Charge
                - Electronic PLD Bonus
                
                **Note:** Make sure none of the titles having "Incentives Off Effective Rates" are missed and all the required information is extracted accurately.
                
                Use the following output schema:
                
                {
                    "table_rows": [
                        {
                            "service": "string", (The UPS Service name as written in the contract file),
                            "billing": "string",
                            "zone": "string",
                            "weight": "string",
                            "weightUnit": "lbs",
                            "discount": "string" (needs to be fully accurate as written in the contract file),
                            "tags": ["string", ...],
                            "destination": "string or null" // The Destination name if available else null (eg. Saudi Arabia, Egypt, United Arab Emirates, etc.)
                        }
                    ]
                }
                
                If you are sure there are no pending rows to extract then return empty array of table_rows.
                
                Return only 70 rows of extracted data.
        """
        
        while True:
            if len(table["tableData"]["rows"]) > 0:
                last_5_rows = table["tableData"]["rows"][-5:]
                
                incentive_off_effective_rates_extraction_prompt += f"""
                    Continuing from the last extracted rows:
                    {str(last_5_rows)}
                """
            response = cls.rate_limited_call(chat.send_message, incentive_off_effective_rates_extraction_prompt)
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
            
        incentive_off_effective_rates_metadata_prompt = """
            Extract the notes relevant to the given services.
            Extract the validity period for the given services as mentioned in the contract.
            
            Notes are usually located above or below the Incentives Off Effective Rates table of the given services.
            validity period of the given services is usually mentioned in the text below the Incentives Off Effective Rates table of that service.
            
            Extract the Details accurately as mentioned in the contract file.
            
            These are the services for which you need to extract metadata:
            {services}
            
            Use the following output schema:
            
            {
                "metadata": [
                    "service": "string",
                    "notes": ["string", ...], // Relevant notes for this particular service
                    "validityPeriod": {         // Validity period for this particular service
                        "startDate": "string",
                        "endDate": "string"   
                    }
                ]
            }
        """.replace("{services}", ", ".join(set([row["service"] for row in table["tableData"]["rows"]])))
        
        response = cls.rate_limited_call(chat.send_message, incentive_off_effective_rates_metadata_prompt)
        
        try:
            metadata = json.loads(response.text.replace("```json\n", "").replace("\n```", "")).get("metadata", [])
            print("Extracted Metadata for inceintive off effective rates: ", metadata)
        except:
            print("Failed to extract metadata for inceintive off effective rates")
            metadata = []
        
        table["metadata"] = metadata        
            
        return table
    
    @classmethod
    def extract_portfolio_tier_incentive_table(cls, uploadedFile: File):
        chat = model.start_chat(history=[
            {
                'role': "user",
                'parts': [uploadedFile, "Go through the attached contract and answer my questions."]
            }
        ])
        
        response = cls.rate_limited_call(chat.send_message, """
            Locate the Portfolio Tier Incentive Table or any other table which follows a similar format in the attached contract.
            Go through all the 3-4 pages of the Portfolio Tier Incentive Table in the contract file.
            Read all the rows on all the pages of Portfolio Tier Incentive Table.
            Extract the Service names listed in the Portfolio Tier Incentive Table and return them in a structured format.
            
            Additionally, extract the validity period and any relevant notes mentioned in the contract.
            
            Use the following output schema:
            {
                "services": [
                    "string", ... // All Service names found in the Portfolio Tier Incentive Table
                ],
                "validityPeriod": {
                    "startDate": "string",  // Start date extracted from the document
                    "endDate": "string"  // End date extracted from the document
                },
                "notes": ["string", ...] // Any relevant notes from the contract
            }
        """)
        
        try:
            extracted_data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            services = extracted_data.get("services", [])
            validity_period = extracted_data.get("validityPeriod", {"startDate": "", "endDate": ""})
            notes = extracted_data.get("notes", [])
        except:
            print("Failed to extract Service names, validity period, or notes from Portfolio Tier Incentive Table")
            services, validity_period, notes = [], {"startDate": "", "endDate": ""}, []
            
        print("Extracted Portfolio Tier Incentive Table services: ", len(services))
        
        no_of_calls = math.ceil(len(services) / 10)
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
        
        for i in range(no_of_calls):
            services_chunk = services[i*10:(i+1)*10]
            
            response = cls.rate_limited_call(chat.send_message, """
                Find the Portfolio Tier Incentive Table or any other table which follows a similar format from the attached contract.
                Find the following Service(s) in the Portfolio Tier Incentive Table: {service_names}.
                
                For each of the above Service(s), extract the "Land/Zone"(optional) and "WeeklyChargesBands" values.
                
                 Use the following output schema:
                 {
                     "table_rows": [
                         {
                         "service": "string",
                         "land_zone": "string",
                         "bandRange": "string", (range in any of these 2 formats "x - y" or "x and up")
                         "currency": "string" (currency of weekly charges band eg. USD),
                         "discount": "percentage (numeric string, or null)",
                         "tags": ["string", ...] // Relevant tags for the service (e.g., "Letter", "Prepaid", "Import", "Export", "Document", "Package", .....)
                         }
                     ]
                 }
                 The bandRange is "WeeklyChargesBands" and should be strictly in any of these 2 formats "x - y" or "x and up" only
                
                 For each row, ensure the "discount" value is returned as a numeric percentage string (e.g. "0.00%", "18.00%", ...). 
                 If the discount is not numeric, output null.
                
                 **Note:** Extract the "discount" values accurately as written in the contract file based on service and weekly charge band.
            """.replace("{service_names}", ", ".join(services_chunk)))
            
            try:
                table_rows = json.loads(response.text.replace("```json\n", "").replace("\n```", "")).get("table_rows", [])
                print("Extracted Portfolio Tier Incentive Table rows for part ",i,": ",len(table_rows))
            except:
                print("Failed to extract Portfolio Tier Incentive Table rows for part ",i)
                table_rows = []
            
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
                    print(row)
                    print("Error in bandRange")
                    del table_rows[table_rows.index(row)]
            
            table["tableData"]["rows"].extend(table_rows)
            
        return table

    @classmethod
    def extract_minimum_net_charge_tables(cls, chat: ChatSession):
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
                Extract the table if it continues in the next page
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
                    "remaining_tables_count": int,   // Number of tables remaining AFTER this batch
                    "notes": "string" // Extracted notes from the contract
                    "validityPeriod": {{
                        startDate: "string",  // Start date extracted from the document
                        endDate: "string"  // End date extracted from the document
                    }}
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

        def extract_billing_type(service_name):
            if "Prepaid" in service_name:
                return "Prepaid"
            elif "Freight Collect" in service_name:
                return "Freight Collect"
            else:
                return "Unknown"

        def format_combined_table(all_tables, notes, validity_period):
            combined_table = {
                "title": "Minimum Net Charge",
                "tableData": {
                    "headers": ["service", "billing", "zone", "adjustmentDiscount", "tags"],
                    "rows": [],
                    "notes": notes,
                    "validityPeriod": validity_period
                }
            }

            for table in all_tables:
                service_name = table.get("name", "Unknown Service")
                billing_type = extract_billing_type(service_name)
                for row in table.get("data", []):
                    filtered_service_name = " ".join([word for word in service_name.split()[:3] if word.lower() != "to"])
                    combined_table["tableData"]["rows"].append({
                        "service": filtered_service_name,
                        "billing": billing_type,
                        "zone": row["zone"],
                        "adjustmentDiscount": row["incentive"],
                        "tags": [tag for tag in service_name.split()[3:] if tag != "-"]
                    })
            
            return combined_table

        # Start collecting all tables
        all_tables = []
        batch_start = 0
        notes = []
        validity_period = {}
        
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
            notes.append(batch_data.get("notes", ""))
            validity_period.update(batch_data.get("validityPeriod", {}))
            print(f"\nBatch progress:")
            print(f"- Tables in this batch: {len(current_tables)}")
            print(f"- Total tables so far: {len(all_tables)}")
            print(f"- Tables remaining: {remaining_count}")
            
            if remaining_count == 0:
                break
                
            batch_start += len(current_tables)
            
        print(f"\nExtraction completed. Total tables extracted: {len(all_tables)}")
        print(all_tables)
        
        result_table = format_combined_table(all_tables, notes, validity_period)
        # print(result_table)
        
        return result_table
    
    @classmethod
    def extract_service_adjustment_table(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract the table in the attached contract in JSON format that contains all of the following headers:
              1. 'Service'
              2. 'Minimum Per'
              3. 'Zone'
              4. 'Base Rate'
              5. 'Adjustment'
            
            Target only tabular data.
            Skip any table that is missing a header.
            
            There are 2 such tables; extract both and merge their data into one final table.
            
            For the 'adjustment' field, ensure that it is returned as a numeric string (optionally with a leading minus sign) or null if not available.
            Extract the 'Currency' for each row.
            Identify relevant tags for each service (e.g., "Air", "Letter", "Prepaid") or present in the base rate.
            Extract the validity period mentioned in the contract.
            
            Use the following output schema:
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
                            "adjustment": "string (numeric, or null)",
                            "currency": "string" (eg. USD),
                            "tags": ["string", ...] // Relevant tags for the service
                        }
                    ],
                    "notes": [
                        "Service adjustments applied per minimumPer type",
                        "Adjustment values are in specified currency"
                    ],
                    "validityPeriod": {
                        "startDate": "string",  // Start date extracted from the document
                        "endDate": "string"  // End date extracted from the document
                    }  
                }
            }
        """)
        
        try:
            extracted_data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            return extracted_data
        except:
            print("Failed to extract service adjustment table")
            return []


    # @classmethod
    # def extract_additional_handling_charge_table(cls, chat: ChatSession):
    #     response = cls.rate_limited_call(chat.send_message, """
    #         Extract the table in the attached contract in JSON format that has the headers 'Service(s)', 'Land/Zone', and 'Incentives', 
    #         with the title 'Additional Handling Charge ($)'.
            
    #         **# Updated Prompt:**
    #         For the 'incentives' field, return only a numeric percentage string (e.g. "18.00%") or null if not applicable.
            
    #         Use the following output schema:
    #         {
    #             "title": "Additional Handling Charge ($)",
    #             "tableData": [
    #             {
    #                 "service": "string",
    #                 "land/zone": "string",
    #                 "incentives": "percentage (numeric string, or null)"
    #             }
    #             ]
    #         }
    #     """)
    #     print(response.text.replace("```json\n", "").replace("\n```", ""))
    #     print("Data Part 10")
    #     try:
    #         data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
    #         return data.get("table", {})
    #     except:
    #         return []
    
    @classmethod
    def extract_electronic_pld_bonus_table(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract the table in the attached contract in JSON format that has the headers 'Service(s)' and 'Electronic PLD Bonus'.
            
            Ensure that the 'bonus' field is returned as a numeric percentage string (e.g. "18.00%") or null.
            Extract relevant tags for each service (e.g., "Air", "Letter", "Prepaid").
            Extract the validity period mentioned in the contract.
            Extract notes relevant to the Electronic PLD Bonus from the contract.
            
            Use the following output schema:
            {
                "title": "Electronic PLD Bonus",
                "tableData": {
                    "headers": [
                        "service",
                        "bonus",
                        "tags"
                    ],
                    "rows": [
                        {
                            "service": "string",
                            "bonus": "percentage (numeric string, or null)",
                            "tags": ["string", ...] // Relevant tags for the service
                        }
                    ],
                    "notes": [
                        "string", ... // Extracted notes from the contract
                    ],
                    "validityPeriod": {
                        "startDate": "string",  // Start date extracted from the document
                        "endDate": "string"  // End date extracted from the document
                    }  
                }
            }
        """)
        
        try:
            extracted_data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            return extracted_data
        except:
            print("Failed to extract electronic PLD bonus table")
            return []
    
    @classmethod
    def extract_contract_details(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract all addresses from the Account Numbers section of the contract.
            Format each address as a complete object with name, street, city, stateCode, zipCode, and countryCode.
            
            Determine if this is a UPS or FedEx contract based on the content of the attached document.
            
            Additionally, extract the account number and commodity tier for each account.
            
            Use the following output schema:
            {
                "carrier": "string",  // "UPS" or "FedEx"
                "eligible_accounts": [
                    {
                        "account_number": "string",
                        "name": "string",
                        "address": "string",  // Formatted as "Street, City, State, Country"
                        "zip": "string",
                        "commodity_tier": "string"
                    }
                ]
            }
        """)
        
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        
        try:
            data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            return data
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
            extract_service_discounts_future = executor.submit(cls.extract_incentive_off_effective_rates, chat)
            extracted_portfolio_tier_incentives_tables = executor.submit(cls.extract_portfolio_tier_incentive_table, uploadedFile)
            extracted_zone_incentives_tables_future = executor.submit(cls.extract_minimum_net_charge_tables, chat)
            extracted_service_min_per_zone_base_rate_adjustment_table_future = executor.submit(cls.extract_service_adjustment_table, chat)
            extracted_electronic_pld_bonus_table_future = executor.submit(cls.extract_electronic_pld_bonus_table, chat)
            extracted_contract_details_future = executor.submit(cls.extract_contract_details, chat)
            
            extracted_service_discounts_table = extract_service_discounts_future.result()
            extracted_portfolio_tier_incentives_table = extracted_portfolio_tier_incentives_tables.result()
            extracted_zone_incentives_tables = extracted_zone_incentives_tables_future.result()
            extracted_service_min_per_zone_base_rate_adjustment_table = extracted_service_min_per_zone_base_rate_adjustment_table_future.result()
            extracted_electronic_pld_bonus_table = extracted_electronic_pld_bonus_table_future.result()
            extracted_contract_details = extracted_contract_details_future.result()
        
        
        tables = []
        tables.append(extracted_service_discounts_table)
        tables.append(extracted_portfolio_tier_incentives_table)
        tables.append(extracted_zone_incentives_tables)
        tables.append(extracted_service_min_per_zone_base_rate_adjustment_table)
        tables.append(extracted_electronic_pld_bonus_table)
        
        
        return {
            "details": extracted_contract_details,
            "tables": tables,
        }
