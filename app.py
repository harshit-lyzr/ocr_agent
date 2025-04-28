from fastapi import FastAPI, File, UploadFile
import os
import asyncio
import shutil
from pyzerox import zerox
from dotenv import load_dotenv
from ops import calculate_actions
from pagos import deduct_usage, get_organization_id


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
async def extract_pdf(api_key: str, file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the PDF file using py-zerox
        result = await zerox(file_path=file_path, model=MODEL)
        tokens = {
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens
        }
        pages_dict = {
            i + 1: {"page": page.page, "content": page.content} for i, page in enumerate(result.pages)
        }

        # Cleanup: Remove the file after processing
        os.remove(file_path)
        total_actions = calculate_actions("gemini","gemini-1.5-pro", result.input_tokens, result.output_tokens)
        org_id = get_organization_id(api_key)
        deduct_usage(org_id["data"], total_actions)
        return {"status": "success", "data": pages_dict, "total_actions": total_actions}

    except Exception as e:
        return {"status": "error", "message": str(e)}
