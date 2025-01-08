import os
import google.generativeai as genai
from google.generativeai.types.file_types import File
from dotenv import load_dotenv
import json
from fastapi import UploadFile
from google.generativeai import ChatSession

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
    async def extract_weight_destination_zone_bands_incentives(cls, chat: ChatSession):
        response = chat.send_message("""
                          Extract all the tables in the attached contract in json format.
                          DO NOT INCLUDE 'Portfolio Tier Incentive' Table.
                          Start with the first table.
                          Max Table Count to extract is 9.
                          Mention the remaining tables to be extracted.
                          
                          Use the following schemas to structure contract tables based on their purpose and layout.
                          
                          Output Format:
                          {
                              "tables": [
                                {
                                  "table_type": "weight_destination_zone_bands_discount",
                                  "name": "string",
                                  "data": [
                                    { "destination": "string or null", "weight": "string", "zone": "string", "band": "string", "discount": "percentage" }
                                  ]
                                }
                              ],
                              "extracted_tables_count": int,
                              "remaining_tables_count": int
                          }
                          
                          **How to Select**:
                            1. Match the table's structure to the schema fields.
                            2. Match the tables that have any combination of these 5 fields, `weight`, `destination`, `zone`, `band`, and `discount`.
                            3. Zone and Destination are both seperate fields.
                            4. Zone can contain ALL, All, or number strings like 403,693,...
                            5. Destination only contains Place names, like Egypt, SaudiArabia, ...
                            
                            DO NOT EXTRACT DATA WHICH IS NOT IN TABLE FORMAT (like data in one line or sentence format).
                          """)
        
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        
        data_part1 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 1")
        print("Extracted: ",data_part1["extracted_tables_count"])
        print("Remaining: ",data_part1["remaining_tables_count"])
        
        response = chat.send_message("""
                          Extract all the tables in the attached contract in json format.
                          DO NOT INCLUDE 'Portfolio Tier Incentive' Table.
                          Start with the first table.
                          Max Table Count to extract is 9.
                          Mention the remaining tables to be extracted.
                          
                          Use the following schemas to structure contract tables based on their purpose and layout.
                          
                          Output Format:
                          {
                              "tables": [
                                {
                                  "table_type": "weight_destination_zone_bands_discount",
                                  "name": "string",
                                  "data": [
                                    { "destination": "string or null", "weight": "string", "zone": "string", "band": "string", "discount": "percentage" }
                                  ]
                                }
                              ],
                              "extracted_tables_count": int,
                              "remaining_tables_count": int
                          }
                          
                          **How to Select**:
                            1. Match the table's structure to the schema fields.
                            2. Match the tables that have any combination of these 5 fields, `weight`, `destination`, `zone`, `band`, and `discount`.
                            3. Zone and Destination are both seperate fields.
                            4. Zone can contain ALL, All, or number strings like 403,693,...
                            5. Destination only contains Place names, like Egypt, SaudiArabia, ...
                            
                            DO NOT EXTRACT DATA WHICH IS NOT IN TABLE FORMAT (like data in one line or sentence format).
                          """.replace("first",str(data_part1["extracted_tables_count"])))
        
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        
        data_part2 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 2")
        print("Extracted: ",data_part2["extracted_tables_count"])
        print("Remaining: ",data_part2["remaining_tables_count"])
                                     
        
        tables = []
        tables.extend(data_part1["tables"])
        tables.extend(data_part2["tables"])
        return tables   
    
    @classmethod
    async def extract_textual_tables(cls, chat: ChatSession):
        response = chat.send_message("""
                            Extract all the incentives off in text form from the attached contract in json format.
                            
                            Use the following schemas to structure output.
                            
                            Output Format:
                            
                            {
                              "table": 
                                {
                                  "table_type": "textual_incentives",
                                  "name": "string", // Title of the text line.
                                  "data": [
                                    { 
                                        "service": "string", // Name of the service (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                        "discount": "percentage" // Discount percentage (e.g., "-65.00%")
                                    }
                                  ]
                                }
                              ,
                              "extracted_tables_count": int,
                              "remaining_tables_count": int
                          }
                          
                          DO NOT INCLUDE DATA WHICH NODES NOT HAVE MENTIONED DISCOUNTS.
                            """)
        
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        
        data_part1 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 3")
        print("Extracted: ",data_part1["extracted_tables_count"])
        print("Remaining: ",data_part1["remaining_tables_count"])
        
        return [data_part1["table"]  ]   
    
    @classmethod
    async def extract_portfolio_tier_incentives_table(cls, chat: ChatSession):
        
        response = chat.send_message("""
                            Extract Portfolio Tier Incentive Table from the attached contract in json format.
                            
                            Collect Data for First 80 Services in the table.
                            Max Data Count to extract is 80.
                            
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
                                      "discount": "percentage" // Discount percentage (e.g., "18.00%")
                                    }
                                  ]
                                }
                            }
                            
                            """)
        
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 4")
        
        data_part1 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        
        table = data_part1["table"]
        
        response = chat.send_message("""
                            Extract Portfolio Tier Incentive Table from the attached contract in json format.
                            
                            Start Collecting Data from 80th Service in the table.
                            Max Data Count to extract is 80
                            
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
                                      "discount": "percentage" // Discount percentage (e.g., "18.00%")
                                    }
                                  ]
                                }
                            }
                            
                            """)
        
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 5")
        
        data_part2 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        
        response = chat.send_message("""
                            Extract Portfolio Tier Incentive Table from the attached contract in json format.
                            
                            Start Collecting Data from 160th Service in the table.
                            Max Data Count to extract is 80.
                            
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
                                      "discount": "percentage" // Discount percentage (e.g., "18.00%")
                                    }
                                  ]
                                }
                            }
                            
                            
                            """)
        
        print(response.text.replace("```json\n", "").replace("\n```", ""))
        print("Data Part 6")
        
        data_part3 = json.loads(response.text.replace("```json\n", "").replace("\n```", ""))
        
        table["data"].extend(data_part2["table"]["data"])
        
        table["data"].extend(data_part3["table"]["data"])
        
        return [table]
                                                       
                            
    @classmethod
    async def extract_zone_incentives_tables(cls, chat: ChatSession):

        response = chat.send_message("""
                          Extract all the tables in the attached contract in json format.
                          Extract Only the Tables of type 'zone_adjustment'
                          Start with the first table.
                          Max Table Count to extract is 10.
                          Mention the remaining tables to be extracted.
                          
                          Use the following schemas to structure contract tables based on their purpose and layout.
                          
                          Output Format:
                          {{
                              "tables": [
                                {
                                  "table_type": "zone_adjustment",
                                  "name": "string",
                                  "data": [
                                    {
                                      "service": "string",          // Name of the service (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                      "zone": "string",             // Zone (e.g., "081")
                                      "discount": "percentage"    // Adjustment percentage (e.g., "-65.00%")
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
                               - Zone Adjustment → `zone_adjustment`.                          
                          
                          """)

        print(response.text.replace("```json\n", "").replace("\n```", ""))
        
        data_part1 = json.loads(response.text.replace(
            "```json\n", "").replace("\n```", ""))
        
        print("Data Part 7")
        print("Extracted: ",data_part1["extracted_tables_count"])
        print("Remaining: ",data_part1["remaining_tables_count"])
        
        response = chat.send_message("""
                          Extract all the tables in the attached contract in json format.
                          Extract Only the Tables of type 'zone_adjustment'
                          Start with the first table.
                          Max Table Count to extract is 10.
                          Mention the remaining tables to be extracted.
                          
                          Use the following schemas to structure contract tables based on their purpose and layout.
                          
                          Output Format:
                          {{
                              "tables": [
                                {
                                  "table_type": "zone_adjustment",
                                  "name": "string",
                                  "data": [
                                    {
                                      "service": "string",          // Name of the service (e.g., "UPS Worldwide Express - Export - Document - Prepaid")
                                      "zone": "string",             // Zone (e.g., "081")
                                      "adjustment": "percentage"    // Adjustment percentage (e.g., "-65.00%")
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
                               - Zone Adjustment → `zone_adjustment`.                          
                          
                          """.replace("first",str(data_part1["extracted_tables_count"])))

        print(response.text.replace("```json\n", "").replace("\n```", ""))
        
        data_part2 = json.loads(response.text.replace(
            "```json\n", "").replace("\n```", ""))
        
        print("Data Part 8")
        print("Extracted: ",data_part2["extracted_tables_count"])
        print("Remaining: ",data_part2["remaining_tables_count"])

        tables = []
        tables.extend(data_part1["tables"])
        tables.extend(data_part2["tables"])
        return tables
    
    @classmethod
    async def extract(cls, contract: UploadFile):
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
        
        extracted_weight_zone_incentives_tables = await cls.extract_weight_destination_zone_bands_incentives(chat)
        extracted_textual_tables = await cls.extract_textual_tables(chat)
        extracted_portfolio_tier_incentives_tables = await cls.extract_portfolio_tier_incentives_table(chat)
        extracted_zone_incentives_tables = await cls.extract_zone_incentives_tables(chat)
        
        tables = []
        tables.extend(extracted_weight_zone_incentives_tables)
        tables.extend(extracted_textual_tables)
        tables.extend(extracted_portfolio_tier_incentives_tables)
        tables.extend(extracted_zone_incentives_tables)
        return tables
