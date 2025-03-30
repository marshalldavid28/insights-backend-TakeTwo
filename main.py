from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from data_processing import process_uploaded_file

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    from io import BytesIO
    df_bytes = BytesIO(content)

    result, error = process_uploaded_file(df_bytes)
    if error:
        return JSONResponse(status_code=400, content={"error": error})

    result["source_file"] = file.filename
    return JSONResponse(content=result)
