import os
import google.generativeai as genai
from google.generativeai.types.file_types import File
from dotenv import load_dotenv
import json
from fastapi import UploadFile
from google.generativeai import ChatSession
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Create the model
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel("gemini-2.0-flash-exp")

class ContractDataExtractionService:
    
    @classmethod
    def extract_weight_destination_zone_bands_incentives(cls, chat: ChatSession):
        response = chat.send_message("""
                          Extract all the tables in the attached contract in json format which match with following conditions:
                            1. Table has 'Weight (lbs)', 'Zones' and 'Discount' columns. Table Type: `weight_zone_incentive`
                            2. Table has 'Zones', 'Bands ($)'and 'Discount' columns. Table Type: `zone_bands_incentive`
                            3. Table has 'Zones' and 'Discount' columns. Table Type: `zone_incentive`
                            4. Table has 'Destination', 'Zone' and 'Discount' columns. Table Type: `destination_zone_incentive`
                            5. Table has 'Destination', 'Zone', 'Weight' and 'Discount' columns. Table Type: `destination_zone_weight_incentive`
                            
                          Data not displayed in tabular format should be ignored.
                          Data not following above conditions should be ignored.
                          Do not merge separate tables into one.
                          Go in the order of the tables in the contract.
                          
                          Start with the first 4 tables.
                          Table Count to extract is exactly 4 tables.
                          
                          Use the following schemas to structure contract tables based on their purpose and layout.
                          
                          Output Format:
                          {
                              "tables": [
                                {
                                  "table_type": "table_type", // From the above list of table types
                                  "name": "string", // Full Table Name (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                  "data": [
                                    { 
                                      "destination": "string or null", // Destination (e.g., "Egypt", "SaudiArabia", ...). If not available, then null.
                                      "weight": "string", // Weight (e.g., "1-5", "6-10", "0-999" ...)
                                      "zone": "string", // Zone (e.g., "ALL", "403", "693", ...)
                                      "band": "string", // Weekly Charges Band Range ($) (e.g., "0.01 - 19,429.99", ...)
                                      "incentive": "percentage" // Discount percentage (e.g., "18.00%")
                                    }
                                  ]
                                }
                              ]
                          }                            
                            
                          **Tables to Exclude**:
                            1. Portfolio Tier Incentives
                            2. Zone Adjustment
                            3. Additional Handling Charge
                            4. Electronic PLD Bonus
                          """)
        
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        
        try:
          data_part1 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        except:
          return []
        print("Data Part 1")
        print(len(data_part1["tables"]))
        
        response = chat.send_message("""
                          Extract all the tables in the attached contract in json format which match with following conditions:
                            1. Table has 'Weight (lbs)', 'Zones' and 'Discount' columns. Table Type: `weight_zone_incentive`
                            2. Table has 'Zones', 'Bands ($)'and 'Discount' columns. Table Type: `zone_bands_incentive`
                            3. Table has 'Zones' and 'Discount' columns. Table Type: `zone_incentive`
                            4. Table has 'Destination', 'Zone' and 'Discount' columns. Table Type: `destination_zone_incentive`
                            5. Table has 'Destination', 'Zone', 'Weight' and 'Discount' columns. Table Type: `destination_zone_weight_incentive`
                            
                          A table is valid if it follows any one of the above conditions.
                          To Validate a condition it should have all the columns mentioned in the condition. 
                          Data not following above conditions should be ignored.
                          Do not merge separate tables into one.
                          Do not split a single table into multiple tables.
                          Go in the order of the tables in the contract.
                          
                          Start with the 6th table of the contract (UPS World wide Express® - Export - Pak - Prepaid All - Incentives Off Effective Rates).
                          End with the table having title 'UPS World wide Expedited® - Export - Package - Prepaid All'
                          
                          Use the following schemas to structure contract tables based on their purpose and layout.
                          
                          Output Format:
                          {
                              "tables": [
                                {
                                  "table_type": "table_type", // From the above list of table types
                                  "name": "string", // Full Table Name (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                  "data": [
                                    { 
                                      "destination": "string or null", // Destination (e.g., "Egypt", "SaudiArabia", ...). If not available, then null.
                                      "weight": "string", // Weight (e.g., "1-5", "6-10", "0-999" ...)
                                      "zone": "string", // Zone (e.g., "ALL", "403", "693", ...)
                                      "band": "string", // Weekly Charges Band Range ($) (e.g., "0.01 - 19,429.99", ...)
                                      "incentive": "percentage" // Discount percentage (e.g., "18.00%")
                                    }
                                  ]
                                }
                              ]
                          }                            
                            
                          **Tables to Exclude**:
                            0. Having only a single line title without any tablular representation data.
                            1. Portfolio Tier Incentives
                            2. Zone Adjustment
                            3. Additional Handling Charge
                            4. Electronic PLD Bonus
                          """)
        
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        
        try:
          data_part2 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        except:
          return data_part1["tables"]
        print("Data Part 2")
        print(len(data_part2["tables"]))
                                     
        
        tables = []
        tables.extend(data_part1["tables"])
        tables.extend(data_part2["tables"])
        return tables   
    
    @classmethod
    def extract_service_incentive_tables(cls, chat: ChatSession):
        response = chat.send_message("""
                            Extract all the incentives mentioned in textual form from the attached contract in json format.
                            Skip all the tabular data strictly.
                            
                            Use the following schemas to structure output.
                            
                            Output Format:
                            
                            {
                              "table": 
                                {
                                  "table_type": "service_incentives",
                                  "name": "Service Incentives",
                                  "data": [
                                    { 
                                        "service": "string", // Name of the service (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                        "incentive": "percentage" // Discount percentage only no string or text (e.g., "-65.00%")
                                    }
                                  ]
                                }
                          }
                          
                          DO NOT INCLUDE DATA WHICH NODES NOT HAVE MENTIONED DISCOUNTS VALUES.
                            """)
        
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        
        try:
          data_part1 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        except:
          return []
        print("Data Part 3")
        
        return [data_part1["table"]]   
    
    @classmethod
    def extract_portfolio_tier_incentives_table(cls, chat: ChatSession):
        
        response = chat.send_message("""
                            Extract Portfolio Tier Incentive Table from the attached contract in json format.
                            
                            Extract All 38 Service(s) for First 2 Weekly Charges Bands only (ie, 76 data entries total).
                            
                            Use the following schemas to structure output.
                            
                            Output Format:
                            
                            {
                                "table":
                                {
                                  "table_type": "portfolio_tier_incentives",
                                  "name": "string",
                                  "data": [
                                    {
                                      "service": "string", // Name of the service (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                      "land/zone": "string", // Land or Zone (e.g., "ALL", "403", "693", ...)
                                      "band": "string", // Band Range (e.g., "0.01 - 19,429.99", ...)
                                      "incentive": "percentage" // Discount percentage (e.g., "18.00%")
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
        
        table = data_part1["table"]
      
        print(len(data_part1["table"]["data"]))
        
        response = chat.send_message("""
                            Extract Portfolio Tier Incentive Table from the attached contract in json format.
                            
                            Extract All 38 Service(s) for Next 2 Weekly Charges Bands only (ie, 76 data entries total).
                            
                            Use the following schemas to structure output.
                            
                            Output Format:
                            
                            {
                                "table":
                                {
                                  "table_type": "portfolio_tier_incentives",
                                  "name": "string",
                                  "data": [
                                    {
                                      "service": "string", // Name of the service (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                      "land/zone": "string", // Land or Zone (e.g., "ALL", "403", "693", ...)
                                      "band": "string", // Band Range (e.g., "0.01 - 19,429.99", ...)
                                      "incentive": "percentage" // Discount percentage (e.g., "18.00%")
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
        print(len(data_part2["table"]["data"]))
        
        table["data"].extend(data_part2["table"]["data"])
        
        response = chat.send_message("""
                            Extract Portfolio Tier Incentive Table from the attached contract in json format.
                            
                            Extract All 38 Service(s) for Next 2 Weekly Charges Bands only (ie, 76 data entries total).
                            
                            Use the following schemas to structure output.
                            
                            Output Format:
                            
                            {
                                "table":
                                {
                                  "table_type": "portfolio_tier_incentives",
                                  "name": "string",
                                  "data": [
                                    {
                                      "service": "string", // Name of the service (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                      "land/zone": "string", // Land or Zone (e.g., "ALL", "403", "693", ...)
                                      "band": "string", // Band Range (e.g., "0.01 - 19,429.99", ...)
                                      "incentive": "percentage" // Discount percentage (e.g., "18.00%")
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
        print(len(data_part3["table"]["data"]))
        
        table["data"].extend(data_part3["table"]["data"])
        
        return [table]
                                                       
                            
    @classmethod
    def extract_zone_incentives_tables(cls, chat: ChatSession):

        response = chat.send_message("""
                          Extract all the tables in the attached contract in json format.
                          Extract Only the Tables of type 'zone_incentive'
                          Start with the first table.
                          Max Table Count to extract is 10.
                          Mention the remaining tables to be extracted.
                          
                          Use the following schemas to structure contract tables based on their purpose and layout.
                          
                          Output Format:
                          {{
                              "tables": [
                                {
                                  "table_type": "zone_incentive",
                                  "name": "string",
                                  "data": [
                                    {
                                      "zone": "string",             // Zone (e.g., "081")
                                      "incentive": "percentage"    // Adjustment percentage (e.g., "-65.00%")
                                    }
                                  ]
                                }
                              ],
                              "extracted_tables_count": int,
                              "remaining_tables_count": int
                          }}
                          
                          **How to Select**:
                            1. Match the table's structure to the schema fields.
                            2. Use appropriate schema based on the table's purpose:
                               - Zone Adjustment → `zone_incentive`.                          
                          
                          """)

        print(response.text.replace("```json\n", "").replace("\n```", ""))
        
        try:
          data_part1 = json.loads(response.text.replace(
            "```json\n", "").replace("\n```", ""))
        except:
          return []
        
        print("Data Part 7")
        print("Extracted: ",data_part1["extracted_tables_count"])
        print("Remaining: ",data_part1["remaining_tables_count"])
        
        response = chat.send_message("""
                          Extract all the tables in the attached contract in json format.
                          Extract Only the Tables of type 'zone_incentive'
                          Start with the first table.
                          Max Table Count to extract is 10.
                          Mention the remaining tables to be extracted.
                          
                          Use the following schemas to structure contract tables based on their purpose and layout.
                          
                          Output Format:
                          {{
                              "tables": [
                                {
                                  "table_type": "zone_incentive",
                                  "name": "string",
                                  "data": [
                                    {
                                      "zone": "string",             // Zone (e.g., "081")
                                      "incentive": "percentage"    // Adjustment percentage (e.g., "-65.00%")
                                    }
                                  ]
                                }
                              ],
                              "extracted_tables_count": int,
                              "remaining_tables_count": int
                          }}
                          
                          **How to Select**:
                            1. Match the table's structure to the schema fields.
                            2. Use appropriate schema based on the table's purpose:
                               - Zone Adjustment → `zone_incentive`.                          
                          
                          """.replace("first",str(data_part1["extracted_tables_count"])))

        print(response.text.replace("```json\n", "").replace("\n```", ""))
        
        try:
          data_part2 = json.loads(response.text.replace(
            "```json\n", "").replace("\n```", ""))
        except:
          return data_part1["tables"]
        
        print("Data Part 8")
        print("Extracted: ",data_part2["extracted_tables_count"])
        print("Remaining: ",data_part2["remaining_tables_count"])

        tables = []
        tables.extend(data_part1["tables"])
        tables.extend(data_part2["tables"])
        return tables
      
    @classmethod
    def extract_service_min_per_zone_base_rate_adjustment_table(cls, chat: ChatSession):
      
      response = chat.send_message("""
                            Extract the table having all the following headers from the attached contract in json format.
                              1. 'Service' 
                              2. 'Minimum Per'
                              3. 'Zone'
                              4. 'Base Rate'
                              5. 'Adjustment'
                            
                            Target Only Tabular Data.
                            Skip the table if it has even a single missing header from above.
                            
                            Use the following schemas to structure output.
                            
                            Output Format:
                            
                            {
                                "table":
                                {
                                  "table_type": "service_min_per_zone_base_rate_adjustment",
                                  "name": "Minimum Net Charge",
                                  "data": [
                                    {
                                      "service": "string", // Name of the service (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                      "min_per": "string", // Minimum Per (e.g., "0.01")
                                      "zone": "string", // Zone (e.g., "081")
                                      "base_rate": "string", // Base Rate (e.g., "0.01")
                                      "adjustment": "string or null" // Adjustment string (e.g., "-65.00")
                                    }
                                  ]
                                }
                            }
                            
                            """)
      
      print(response.text.replace("```json\n", "").replace("\n```", ""))
      print("Data Part 9")
      
      try:
        data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        return [data["table"]]
      except:
        return []
    
    @classmethod
    def extract_additional_handling_charge_table(cls, chat: ChatSession):
      
      response = chat.send_message("""
                            Extract the table having the headers 'Service(s)', 'Land/Zone', 'Incentives', with the title 'Additional Handling Charge ($)'
                            from the attached contract in json format.
                            
                            Use the following schemas to structure output.
                            
                            Output Format:
                            
                            {
                                "table":
                                {
                                  "table_type": "additional_handling_charge",
                                  "name": "string",
                                  "data": [
                                    {
                                      "service": "string", // Name of the service (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                      "land/zone": "string", // Land or Zone (e.g., "ALL", "403", "693", ...)
                                      "incentives": "string" // Incentives (e.g., "18.00%")
                                    }
                                  ]
                                }
                            }
                            
                            """)
      
      print(response.text.replace("```json\n", "").replace("\n```", ""))
      print("Data Part 10")
      
      try:
        data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        return [data["table"]]
      except:
        return []
    
    @classmethod
    def extract_electronic_pld_bonus_table(cls, chat: ChatSession):
      
      response = chat.send_message("""
                            Extract the table having the headers 'Service(s)' & 'Electronic PLD Bonus'
                            from the attached contract in json format.
                            
                            Use the following schemas to structure output.
                            
                            Output Format:
                            
                            {
                                "table":
                                {
                                  "table_type": "electronic_pld_bonus",
                                  "name": "string", // Title of the table (e.g., "Electronic PLD Bonus")
                                  "data": [
                                    {
                                      "service": "string", // Name of the service (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                      "electronic_pld_bonus": "string" // Electronic PLD Bonus (e.g., "18.00%")
                                    }
                                  ]
                                }
                            }
                            
                            """)
      
      print(response.text.replace("```json\n", "").replace("\n```", ""))
      print("Data Part 11")
      
      try:
        data = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        return [data["table"]]
      except:
        return []
    
    @classmethod
    def extract(cls, contract: UploadFile):
        # uploadedFile = genai.upload_file(
        #     contract.file, mime_type=contract.content_type)
        uploadedFile = File({
            'name': 'files/58b847xaxn35',
            'display_name': '',
            'mime_type': 'application/pdf',
            'sha256_hash': 'MGQzNTVkNTA1NWFjZmEzMDAwYWEzYThkNjRhNTA4ZTlmMDlmOWE0M2Q1ZTgxY2U3OGVlNjM2OTkyYWQ5OTk0MA==',
            'size_bytes': '152520',
            'state': 'ACTIVE',
            'uri': 'https://generativelanguage.googleapis.com/v1beta/files/58b847xaxn35',
            'create_time': '2025-01-08T09:30:44.476571Z',
            'expiration_time': '2025-01-10T09:30:44.463407310Z',
            'update_time': '2025-01-08T09:30:44.476571Z'
        })
        print(uploadedFile.name)
        
        chat = model.start_chat(history=[
            {
                'role': "user",
                'parts': [uploadedFile,
                          """
                          Go through the attached contract and answer my questions.
                          """]
            }
        ])
        
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
        
        tables = []
        tables.extend(extracted_weight_zone_incentives_tables)
        tables.extend(extracted_service_incentive_tables)
        tables.extend(extracted_portfolio_tier_incentives_tables)
        tables.extend(extracted_zone_incentives_tables)
        tables.extend(extracted_service_min_per_zone_base_rate_adjustment_table)
        tables.extend(extracted_additional_handling_charge_table)
        tables.extend(extracted_electronic_pld_bonus_table)
        return tables
