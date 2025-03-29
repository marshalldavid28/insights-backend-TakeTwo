# main.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

app = FastAPI()

# Allow frontend on Vercel to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with Vercel domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_reports(
    files: List[UploadFile] = File(...),
    objective: str = Form(...),
    target: str = Form(...),
    budget: str = Form(...),
    dates: str = Form(...)
):
    # For now, just return filenames
    file_names = [file.filename for file in files]
    return {
        "message": "Files received",
        "files": file_names,
        "objective": objective,
        "target": target,
        "budget": budget,
        "dates": dates
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
