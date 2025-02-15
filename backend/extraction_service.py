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
                    or ("table_rows" in data and data["table_rows"])
                    or ("rows" in data and data["rows"])
                    or ("eligible_accounts" in data and data["eligible_accounts"])
                    or ("tableData" in data and data["tableData"])
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
    def incentive_off_executives_null_dest(cls, chat: ChatSession):
        def parse_json_response(response_text, label):
            """ Helper function to parse JSON response safely and log errors """
            if not response_text.strip():  # Handle empty response
                print(f"⚠️ Empty response received in {label}")
                return {}

            try:
                data = json.loads(response_text.replace("```json\n", "").replace("\n```", ""))
                if not isinstance(data, dict):
                    print(f"⚠️ Unexpected format in {label}: Expected dictionary but got {type(data)}")
                    return {}

                return data
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error in {label}: {e}")
                return {}

        # Step 1: Extract Data Part 1
        response = cls.rate_limited_call(chat.send_message, """
            Extract all the tables in the attached contract in JSON format which match the following conditions:
            1. Table heading has '- Incentives Off Effective Rates'.
            2. Table has 'Weight (lbs)', 'Zones', and 'Discount' columns.
            3. Populate the zone number in zone, weight range in weight, and discount percentage in discount.
            
            give max 80 rows in the response
            Format output as the following json structure:
            
            {
                "table_rows": [
                    {
                        "service": "UPS Worldwide Express",  // service name  from table heading
                        "billing": "PrepaidAll",  // billing type can be taken name after Package- Prepaid or Residential Package- Prepaid
                        "zone": "All",  // zone number which is present in each column
                        "weight": "All",   // weight range
                        "weightUnit": "lbs",        // weight unit
                        "discount": "53.00%",            // discount percentage       
                        "tag": "Letter,Export, PrepaidAll",   // extract from service name 
                        "destination": "null"  // destination is null
                    },
                ]
            }
            
            Exclude tables for:
            - Portfolio Tier Incentives
            - Zone Adjustment
            - Additional Handling Charge
            - Electronic PLD Bonus
        """)

        data_part1 = parse_json_response(response.text, "Data Part 1")

        # Extract rows from "effective1"
        tables = data_part1.get("table_rows", [])

        print(f"\n🔹 Data Part 1 Extracted ({len(tables)} rows):\n{json.dumps(tables, indent=2)}")

        # Save Part 1 JSON
        file_path1 = "incentiveOff_effective_noDest1.json"
        with open(file_path1, "w", encoding="utf-8") as json_file:
            json.dump(tables, json_file, indent=2)

        # Step 2: Identify Last Extracted Row
        last_row = tables[-1] if tables else None
        if last_row:
            print(f"\n🔍 Last Extracted Row:\n{json.dumps(last_row, indent=2)}")

        # Step 3: Extract Data Part 2 (Continuing from Last Extracted Row)
        if last_row:
            query_part2 = """
            
                Extract 'Incentives Off Effective Rates' tables :
                    1. Table heading has '- Incentives Off Effective Rates'.
                    2. Table has 'Weight (lbs)', 'Zones', and 'Discount' columns.
                    3. Populate the zone number in zone, weight range in weight, and discount percentage in discount.
                    
                **continuing from**
                - Last row: last_row1
                 
            extract max 80 rows in the response
            Format output as the following json structure:
            {
                "table_rows": [
                    {
                        "service": "UPS Worldwide Express",  // service name  from table heading
                        "billing": "PrepaidAll",  // billing type can be taken name after Package- Prepaid or Residential Package- Prepaid
                        "zone": "5",  // zone number which is present in each column
                        "weight": "All",   // weight range
                        "weightUnit": "lbs",        // weight unit
                        "discount": "53.00%",            // discount percentage       
                        "tag": "Letter,Export, PrepaidAll",   // extract from service name 
                        "destination": "null"  // destination is null
                    },
                ]
            }
                
                Only return rows **AFTER** this row, avoiding duplicates.
            """.replace("last_row1", str(last_row))
            print(query_part2)
        else:
            query_part2 = "Extract Incentive Off effective tables where you left extracting"

        response = cls.rate_limited_call(chat.send_message, query_part2)
        data_part2 = parse_json_response(response.text, "Data Part 2")

        # Extract rows from "effective2"
        additional_rows = data_part2.get("table_rows", [])

        print(f"\n🔹 Data Part 2 Extracted ({len(additional_rows)} rows):\n{json.dumps(additional_rows, indent=2)}")

        # Step 4: Merge Both Parts
        tables.extend(additional_rows)

        # Save Final JSON (Both Parts)
        file_path2 = "incentiveOff_effective_noDest.json"
        with open(file_path2, "w", encoding="utf-8") as json_file:
            json.dump(tables, json_file, indent=2)

        print(f"\n✅ Total Extracted Rows: {len(tables)}")
        print(f"✅ Extracted data saved to {file_path2}")

        return tables


    @classmethod
    def incentive_off_executives_statements(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
                                         
            Extract all the details in the attached contract in JSON format which match the following conditions:
            
               
            ex: UPS Worldwide Express® - Export - Letter - PrepaidAll - Incentives Off Effective Rates - 53.00%
                        
            Important: if statement is not ending with percentage then dont extract that statement
             
             ignore this kind of statement where "- 53.00%" is not present at the end of the statement:
             
             ex: UPS Worldwide Express® - Export - Letter - PrepaidAll - Incentives Off Effective Rates
             
            
             
            Format output as the following json structure:
            
            {
                "table_rows": [
                    {
                        "service": "UPS Worldwide Express",  // service name  from statement
                        "billing": "PrepaidAll",  // billing type can be taken name after Package- Prepaid or Residential Package- Prepaid
                        "zone": "All",  
                        "weight": "All",   
                        "weightUnit": "lbs",        
                        "discount": "53.00%",            // discount percentage       
                        "tag": "Letter,Export, PrepaidAll",   // extract from service name 
                        "destination": "null"  // destination is null
                    },
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
        
    
        tables = []
        tables.extend(data_part1.get("table_rows", []))
        
        file_path2 = "incentiveOff_effective_statements.json"
        with open(file_path2, "w", encoding="utf-8") as json_file:
            json.dump(tables, json_file, indent=2)
            
        return tables


    @classmethod
    def extract_weight_destination_zone_bands_incentives(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract all the tables in the attached contract in JSON format which match the following conditions:
              1. Table has 'Weight (lbs)','Destination', 'Zones', and 'Incentives' columns. 
              2. Table has 'Destination', 'Zone', and 'Incentives' columns. 
              3. Table has 'Zones'  columns.
             
            **# Updated Prompt:**
            For every table row, ensure that the "incentive" value is provided strictly as a numeric percentage string (for example, "18.00%"). 
            If a numeric discount is not available, return null for that field.
            
            Data not shown in a clear tabular format should be ignored.
           
            
            Use the following output schema:
            
            {
                "tables": [
                    {
                        "service": "UPS Worldwide Express",  // service name  from statement
                        "billing": "PrepaidAll",  // billing type can be taken name after Package- Prepaid or Residential Package- Prepaid
                        "zone": "620",  if zone is not available then "All"  
                        "weight": "1-150",    // null if not available
                        "weightUnit": "lbs",        
                        "discount": "53.00%",            // discount percentage       
                        "tag": "Letter,Export, PrepaidAll",   // extract from service name 
                        "destination": "Mexico" 
                    },
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
        
        # response = cls.rate_limited_call(chat.send_message, """
        #     Extract all the tables in the attached contract in JSON format which match the following conditions:
        #       1. Table has 'Weight (lbs)', 'Zones', and 'Discount' columns. (Table Type: `weight_zone_incentive`)
        #       2. Table has 'Zones', 'Bands ($)', and 'Discount' columns. (Table Type: `zone_bands_incentive`)
        #       3. Table has 'Zones' and 'Discount' columns. (Table Type: `zone_incentive`)
        #       4. Table has 'Destination', 'Zone', and 'Discount' columns. (Table Type: `destination_zone_incentive`)
        #       5. Table has 'Destination', 'Zone', 'Weight', and 'Discount' columns. (Table Type: `destination_zone_weight_incentive`)
            
        #     **# Updated Prompt:**
        #     For each row, ensure the "incentive" field is strictly a numeric percentage (e.g. "18.00%"). 
        #     If the incentive is not a valid numeric percentage, output null.
            
        #     Do not merge or split tables.
        #     Process tables in contract order.
            
        #     Start with the 6th table (UPS World wide Express® - Export - Pak - Prepaid All - Incentives Off Effective Rates)
        #     and end with the table titled "UPS World wide Expedited® - Export - Package - Prepaid All".
            
        #     Use the following output schema:
        #     {
        #         "tables": [
        #             {
        #                 "service": "UPS Worldwide Express",  // service name  from statement
        #                 "billing": "PrepaidAll",  // billing type can be taken name after Package- Prepaid or Residential Package- Prepaid
        #                 "zone": "All",  
        #                 "weight": "All",   
        #                 "weightUnit": "lbs",        
        #                 "discount": "53.00%",            // discount percentage       
        #                 "tag": "Letter,Export, PrepaidAll",   // extract from service name 
        #                 "destination": "null"  // destination is null
        #             },
        #         ]
        #     }
            
        #     Exclude:
        #       - Tables with only a title (no tabular data)
        #       - Portfolio Tier Incentives
        #       - Zone Adjustment
        #       - Additional Handling Charge
        #       - Electronic PLD Bonus
        # """)
        # print(response.text.replace("```json\n", "").replace("\n```", ""))
        # try:
        #     data_part2 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        # except:
        #     return data_part1.get("tables", [])
        # print("Data Part 2", len(data_part2.get("tables", [])))
        
        tables = []
        tables.extend(data_part1.get("tables", []))
        # tables.extend(data_part2.get("tables", []))
        return tables


    @classmethod
    def extract_service_incentive_tables(cls, chat: ChatSession):
        response = cls.rate_limited_call(chat.send_message, """
            Extract all the incentives mentioned in textual form (non-tabular) from the attached contract in JSON format.
            ex: UPS Worldwide Express® - Export - Letter - PrepaidAll - Incentives Off Effective Rates - 18.00%
            **# Updated Prompt:**
            For the discount values, output only a numeric percentage string (e.g. "18.00%"). 
            If a discount is not provided as a numeric percentage, output null.
            
            Use the following output schema:
            {
                    "table": [
                        {
                            "service": "UPS Worldwide Express",  // service name  from statement
                            "billing": "PrepaidAll",  // billing type can be taken name after Package- Prepaid or Residential Package- Prepaid
                            "zone": "All",  
                            "weight": "All",   
                            "weightUnit": "lbs",        
                            "discount": "18.00%",            // discount percentage       
                            "tag": "Letter,Export, PrepaidAll",   // extract from service name 
                            "destination": "null"  // destination is null
                        },
                    ]
                }
                
            Do not include any rows that lack a discount value.
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        try:
            data_part1 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        except:
            return []
        file_path2 = "incentiveOff_effective_statements.json"
        
        with open(file_path2, "w", encoding="utf-8") as json_file:
            json.dump(data_part1, json_file, indent=2)
            
        return [data_part1.get("table", {})]


    
    @classmethod
    def extract_portfolio_tier_incentives_table(cls, uploadedFile: File):
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
                    "lane_zone",
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
                
                For each of the above Service(s), extract the "Land/Zone" and "WeeklyChargesBands" values.
                
                 For each row, ensure the "discount" value is returned as a numeric percentage string (e.g. "0.00%", "18.00%", ...). 
                 If the discount is not numeric, output null.
                
                 **Note:** Extract the "discount" values accurately as written in the contract file based on service and weekly charge band.
                
                 Use the following output schema:
                 {
                     "table_rows": [
                         {
                         "service": "string",
                         "land_zone": "string",
                         "band": "string", (Only these are possible Formats: "min - max" or "min and up" - Preserve the white spaces as shown in example)
                         "currency": "string" (currency of weekly charges band eg. USD),
                         "discount": "percentage (numeric string, or null)"
                         }
                     ]
                 }
            """.replace("{service_names}", ", ".join(services_chunk)))
            
            try:
                table_rows = json.loads(response.text.replace("```json\n", "").replace("\n```", "")).get("table_rows", [])
                print("Extracted Portfolio Tier Incentive Table rows for part ",i,": ",len(table_rows))
            except:
                print("Failed to extract Portfolio Tier Incentive Table rows for part ",i)
                table_rows = []
            
            for row in table_rows:
                print(row["band"])
                if row["band"] and "up" in row["band"]:
                    min = row["band"].replace(" and up", "").replace("and Up", "")
                    max = "infinity"
                else:
                    min, max = row["band"].replace("- ", "-").replace(" -","-").split("-")
                row["weeklySpendMin"] = min
                row["weeklySpendMax"] = max
                del row["band"]    
            
            table["tableData"]["rows"].extend(table_rows)
            
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
        
        return [result_table]
    
    # @classmethod
    # def extract_zone_incentives_tables(cls, chat: ChatSession):
    #     def process_response(response_text, part_number):
    #         print(response_text)
    #         try:
    #             data = json.loads(response_text.replace("```json\n", "").replace("\n```", ""))
    #             print(f"Data Part {part_number}")
    #             print(f"Extracted:", data.get("extracted_tables_count"))
    #             print(f"Remaining:", data.get("remaining_tables_count"))
    #             return data
    #         except json.JSONDecodeError as e:
    #             print(f"Error parsing JSON response: {str(e)}")
    #             return None

    #     def try_extract_batch(batch_start, max_retries=3):
    #         for attempt in range(1, max_retries + 1):
    #             prompt = f"""
    #             Locate the Minimum Net Charge header in the attached contract.
    #             Under the Minimum Net Charge section,
    #             Extract the next batch of zone adjustment incentive tables from the contract, ensuring the format matches the schema below.
                
    #             Tables contain:
    #             - Service name (first three words)
    #             - Billing type (e.g., Prepaid)
    #             - Zone codes (e.g. "081", "082", "083", etc.)
    #             - Adjustment Discount percentages
    #             - Extract tags from each service name (everything after the first three words)
    #             - Extract the validity period mentioned in the contract
    #             - Extract relevant notes from the contract
                
    #             Important batch processing rules:
    #             1. Process up to 10 complete tables per batch
    #             2. Include exact zone codes as shown in the contract
    #             3. Count remaining tables after this batch
    #             4. Combine all extracted tables into a single unified table
                
    #             Ensure:
    #             - "adjustmentDiscount" is formatted as a numeric percentage string (e.g., "-65.00%")
    #             - Use null for non-numeric adjustment values
    #             - Extract the correct "billing" type
    #             - Extract non-empty notes and validity period
                
    #             Use this exact output schema:
    #             {{
    #                 "title": "Minimum Net Charge",
    #                 "tableData": {{
    #                     "headers": [
    #                         "service",
    #                         "billing",
    #                         "zone",
    #                         "adjustmentDiscount",
    #                         "tags"
    #                     ],
    #                     "rows": [
    #                         {{
    #                             "service": "string",
    #                             "billing": "string",
    #                             "zone": "string",
    #                             "adjustmentDiscount": "percentage (numeric string, or null)",
    #                             "tags": ["string", ...] // Relevant tags for the service
    #                         }}
    #                     ],
    #                     "notes": [
    #                         "string", ... // Extracted notes from the contract
    #                     ],
    #                     "validityPeriod": {{
    #                         "startDate": "string",  // Start date extracted from the document
    #                         "endDate": "string"  // End date extracted from the document
    #                     }}
    #                 }}
    #             }}
    #             """
                
    #             print(f"Calling API, attempt {attempt}")
    #             response = cls.rate_limited_call(chat.send_message, prompt)
                
    #             if not response.text.strip():
    #                 print(f"Received empty or incomplete data on attempt {attempt}, retrying...")
    #                 continue
                    
    #             try:
    #                 data = process_response(response.text, batch_start)
    #                 if data and data.get("tableData"):  
    #                     return data
    #             except Exception as e:
    #                 print(f"Error processing response on attempt {attempt}: {str(e)}")
                    
    #         return None

    #     # Collect all extracted rows into a single table
    #     unified_table = {
    #         "title": "Minimum Net Charge",
    #         "tableData": {
    #             "headers": [
    #                 "service",
    #                 "billing",
    #                 "zone",
    #                 "adjustmentDiscount",
    #                 "tags"
    #             ],
    #             "rows": [],
    #             "notes": [],
    #             "validityPeriod": {"startDate": "", "endDate": ""}
    #         }
    #     }
    #     batch_start = 0
        
    #     while True:
    #         batch_data = try_extract_batch(batch_start)
    #         if not batch_data:
    #             break
    #         print(batch_data)
            
    #         if batch_data["tableData"].get("rows"):
    #             unified_table["tableData"]["rows"].extend(batch_data["tableData"]["rows"])
            
    #         if batch_data["tableData"].get("notes"):
    #             unified_table["tableData"]["notes"].extend(batch_data["tableData"]["notes"])
            
    #         if not unified_table["tableData"]["validityPeriod"]["startDate"] and batch_data["tableData"].get("validityPeriod", {}).get("startDate"):
    #             unified_table["tableData"]["validityPeriod"] = batch_data["tableData"].get("validityPeriod", {"startDate": "", "endDate": ""})
            
    #         remaining_count = batch_data.get("remaining_tables_count", 0)
            
    #         print(f"\nBatch progress:")
    #         print(f"- Total rows so far: {len(unified_table['tableData']['rows'])}")
    #         print(f"- Tables remaining: {remaining_count}")
            
    #         if remaining_count == 0:
    #             break
            
    #         batch_start += 10
        
    #     print(f"\nExtraction completed. Total rows extracted: {len(unified_table['tableData']['rows'])}")
    #     return [unified_table]


    
    
    # @classmethod
    # def extract_service_min_per_zone_base_rate_adjustment_table(cls, chat: ChatSession):
    #     response = cls.rate_limited_call(chat.send_message, """
    #         Extract the table in the attached contract in JSON format that contains all of the following headers:
    #           1. 'Service'
    #           2. 'Minimum Per'
    #           3. 'Zone'
    #           4. 'Base Rate'
    #           5. 'Adjustment'
            
    #         Target only tabular data.
    #         Skip any table that is missing a header.
            
    #         There are 2 such tables; extract both and merge its data into one final table.
            
    #         **# Updated Prompt:**
    #         For the 'adjustment' field, ensure that it is returned as a numeric string (optionally with a leading minus sign) or null if not available.
            
    #         Use the following output schema:
    #         {
    #             "table": {
    #               "table_type": "service_min_per_zone_base_rate_adjustment",
    #               "name": "Minimum Net Charge",
    #               "data": [
    #                 {
    #                   "service": "string",
    #                   "min_per": "string",
    #                   "zone": "string",
    #                   "base_rate": "string",
    #                   "adjustment": "string (numeric, or null)"
    #                 }
    #               ]
    #             }
    #         }
    #     """)
    #     print(response.text.replace("```json\n", "").replace("\n```", ""))
    #     print("Data Part 9")
    #     try:
    #         data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
    #         return [data.get("table", {})]
    #     except:
    #         return []
    
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
            return [extracted_data]
        except:
            print("Failed to extract service adjustment table")
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
                "title": "Additional Handling Charge ($)",
                "tableData": [
                {
                    "service": "string",
                    "land/zone": "string",
                    "incentives": "percentage (numeric string, or null)"
                }
                ]
            }
        """)
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 10")
        try:
            data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
            return [data.get("table", {})]
        except:
            return []

    # @classmethod
    # def extract_electronic_pld_bonus_table(cls, chat: ChatSession):
    #     response = cls.rate_limited_call(chat.send_message, """
    #         Extract the table in the attached contract in JSON format that has the headers 'Service(s)' and 'Electronic PLD Bonus'.
            
    #         **# Updated Prompt:**
    #         Ensure that the 'electronic_pld_bonus' field is returned as a numeric percentage string (e.g. "18.00%") or null.
            
    #         Use the following output schema:
    #         {
    #             "table": {
    #               "table_type": "electronic_pld_bonus",
    #               "name": "string",
    #               "data": [
    #                 {
    #                   "service": "string",
    #                   "electronic_pld_bonus": "percentage (numeric string, or null)"
    #                 }
    #               ]
    #             }
    #         }
    #     """)
    #     print(response.text.replace("```json\n", "").replace("\n```", ""))
    #     print("Data Part 11")
    #     try:
    #         data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
    #         return [data.get("table", {})]
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
            return [extracted_data]
        except:
            print("Failed to extract electronic PLD bonus table")
            return []


    # @classmethod
    # def extract_address(cls, chat: ChatSession):
    #     response = cls.rate_limited_call(chat.send_message, """
    #         Extract ALL the addresses from the Account Numbers section of the contract in JSON format.
    #         Format each address as a complete object (with street number, street, city, stateCode, zipCode, and countryCode).
            
    #         Use the following output schema:
    #         {
    #             "addresses": [
    #                 {
    #                     "name": "string",
    #                     "street": "string",
    #                     "city": "string",
    #                     "stateCode": "string",
    #                     "zipCode": "string",
    #                     "countryCode": "US"
    #                 }
    #             ]
    #         }
    #     """)
    #     print(response.text.replace("```json\n", "").replace("\n```", ""))
    #     try:
    #         data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
    #         addresses = data.get("addresses", [])
    #         return addresses if addresses else None
    #     except:
    #         return None

    # @classmethod
    # def extract_contract_type(cls, chat: ChatSession):
    #     response = cls.rate_limited_call(chat.send_message, """
    #         Determine if this is a UPS or FedEx contract based on the content of the attached document.
    #         Return only "ups" or "fedex" in lowercase.
            
    #         Use the following output schema:
    #         {
    #             "contract_type": "string"
    #         }
    #     """)
    #     print(response.text.replace("```json\n", "").replace("\n```", ""))
    #     try:
    #         data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
    #         return data.get("contract_type", None)
    #     except:
    #         return None
    
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
        
        # extracted_portfolio_tier_incentives_tables = cls.extract_portfolio_tier_incentives_table(uploadedFile)
        
        # Execute all extractions concurrently
        with ThreadPoolExecutor() as executor:
            # extracted_portfolio_tier_incentives_tables = executor.submit(cls.extract_portfolio_tier_incentives_table, uploadedFile)
            # extracted_weight_zone_incentives_tables_future = executor.submit(cls.incentive_off_executives_null_dest, chat)
            extracted_weight_zone_incentives_tables_future = executor.submit(cls.extract_weight_destination_zone_bands_incentives, chat)
            # extracted_service_incentive_tables_future = executor.submit(cls.incentive_off_executives_statements, chat)
            # extracted_service_incentive_tables_future = executor.submit(cls.extract_service_incentive_tables, chat)
            # extracted_zone_incentives_tables_future = executor.submit(cls.extract_zone_incentives_tables, chat)
            # extracted_service_min_per_zone_base_rate_adjustment_table_future = executor.submit(cls.extract_service_min_per_zone_base_rate_adjustment_table, chat)
            # extracted_additional_handling_charge_table_future = executor.submit(cls.extract_additional_handling_charge_table, chat)
            # extracted_electronic_pld_bonus_table_future = executor.submit(cls.extract_electronic_pld_bonus_table, chat)
            
            # extracted_portfolio_tier_incentives_tables = extracted_portfolio_tier_incentives_tables.result()
            extracted_weight_zone_incentives_tables = extracted_weight_zone_incentives_tables_future.result()
            # extracted_service_incentive_tables = extracted_service_incentive_tables_future.result()
            # extracted_zone_incentives_tables = extracted_zone_incentives_tables_future.result()
            # extracted_service_min_per_zone_base_rate_adjustment_table = extracted_service_min_per_zone_base_rate_adjustment_table_future.result()
            # extracted_additional_handling_charge_table = extracted_additional_handling_charge_table_future.result()
            # extracted_electronic_pld_bonus_table = extracted_electronic_pld_bonus_table_future.result()
        
        # with ThreadPoolExecutor() as executor:
        #     extracted_address_future = executor.submit(cls.extract_address, chat)
        #     extracted_contract_details_future = executor.submit(cls.extract_contract_details, chat)
            
        #     extracted_address = extracted_address_future.result()
        #     extracted_contract_details = extracted_contract_details_future.result()
        
        
        # print("Extracted Contract Type:", extracted_contract_details)
        tables = []
        # tables.append(extracted_contract_details)
        tables.extend(extracted_weight_zone_incentives_tables)
        # tables.extend(extracted_service_incentive_tables)
        # tables.extend(extracted_portfolio_tier_incentives_tables)
        # tables.extend(extracted_zone_incentives_tables)
        # tables.extend(extracted_service_min_per_zone_base_rate_adjustment_table)
        # tables.extend(extracted_additional_handling_charge_table)
        # tables.extend(extracted_electronic_pld_bonus_table)
        
        # print("Extracted Address:", extracted_address)
        return {
            "tables": tables,
            # "address": extracted_address,
            # "contract_type": extracted_contract_type
        }
