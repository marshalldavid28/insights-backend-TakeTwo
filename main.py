from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from data_processing import process_uploaded_file
import uvicorn

app = FastAPI()

# --- Enable CORS for frontend access ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your Vercel domain later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Upload endpoint with processor integration ---
@app.post("/upload/")
async def upload_reports(
    files: List[UploadFile] = File(...),
    objective: str = Form(...),
    target: str = Form(...),
    budget: str = Form(...),
    dates: str = Form(...)
):
    summaries = []
    errors = []

    for file in files:
        result, error = process_uploaded_file(file)
        if result:
            summaries.append(result)
        else:
            errors.append({"file": file.filename, "error": error})

    return {
        "message": "Files processed",
        "objective": objective,
        "target": target,
        "budget": budget,
        "dates": dates,
        "summaries": summaries,
        "errors": errors
    }

# --- For local development only ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
