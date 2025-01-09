from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile

from extraction_service import ContractDataExtractionService

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.get("/")
async def read_root():
    return JSONResponse(content={"success": True, "message": "Server is running"})


@app.post("/api/extract")
async def extract(file: UploadFile = File(...)):

    extracted_data = ContractDataExtractionService.extract(file)
    return JSONResponse(content={"success": True, "message": "Extracted data", "tables": extracted_data})
