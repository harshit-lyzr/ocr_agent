from fastapi import FastAPI, File, UploadFile
import os
import asyncio
import shutil
from pyzerox import zerox
from dotenv import load_dotenv


load_dotenv()
app = FastAPI()

# Set Gemini API Key
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

# Model to be used
MODEL = "gemini/gemini-1.5-pro"

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure upload directory exists


@app.get("/")
async def read_root():
    return {"message": "PDF Extraction API is running!"}


@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the PDF file using py-zerox
        result = await zerox(file_path=file_path, model=MODEL)
        pages_dict = {
            i + 1: {"page": page.page, "content": page.content} for i, page in enumerate(result.pages)
        }

        # Cleanup: Remove the file after processing
        os.remove(file_path)

        return {"status": "success", "data": pages_dict}

    except Exception as e:
        return {"status": "error", "message": str(e)}
