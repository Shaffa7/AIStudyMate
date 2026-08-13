import os
import shutil

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel
from pypdf import PdfReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

# -----------------------------
# Load Environment Variables
# -----------------------------

load_dotenv()

print("API Key Loaded:", bool(os.getenv("GEMINI_API_KEY")))

# -----------------------------
# Gemini Client
# -----------------------------

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# -----------------------------
# FastAPI App & Global Variables
# -----------------------------

app = FastAPI()

pdf_text = ""


# -----------------------------
# Enable CORS
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Request Model
# -----------------------------

class Question(BaseModel):
    question: str


# -----------------------------
# PDF Text Extraction
# -----------------------------

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


# -----------------------------
# Home Route
# -----------------------------

@app.get("/")
def home():
    return {"message": "AI StudyMate Backend Running Successfully"}


# -----------------------------
# AI Chat
# -----------------------------

@app.post("/chat")
def chat(data: Question):
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=data.question,
        )
        return {"answer": response.text}
    except Exception as e:
        return {"answer": str(e)}


# -----------------------------
# Upload PDF
# -----------------------------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global pdf_text

    os.makedirs("uploads", exist_ok=True)
    filepath = os.path.join("uploads", file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pdf_text = extract_text_from_pdf(filepath)

    return {"message": "PDF uploaded successfully."}


# -----------------------------
# AI Summary
# -----------------------------

@app.get("/summary")
def summary():
    global pdf_text

    if pdf_text == "":
        return {"summary": "Please upload a PDF first."}

    prompt = f"""
You are an expert teacher.

Read the following study material and generate:
1. Short summary
2. Important points
3. Simple explanation for students

Study Material:
{pdf_text[:30000]}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    return {"summary": response.text}


# -----------------------------
# MCQ Generator
# -----------------------------

@app.get("/mcq")
def generate_mcq():
    global pdf_text

    if pdf_text == "":
        return {"mcq": "Please upload a PDF first."}

    prompt = f"""
You are an experienced university professor.

Generate 10 Multiple Choice Questions.

Rules:
- Four options
- Mention correct answer
- Cover different topics
- Use Markdown formatting

Study Material:
{pdf_text[:30000]}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    return {"mcq": response.text}


# -----------------------------
# Flashcards Generator
# -----------------------------

@app.get("/flashcards")
def flashcards():
    global pdf_text

    if pdf_text == "":
        return {"flashcards": "Please upload a PDF first."}

    prompt = f"""
Create 10 study flashcards.

Format:
## Flashcard 1
Question:
Answer:

Study Material:
{pdf_text[:30000]}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    return {"flashcards": response.text}


# -----------------------------
# Download Notes PDF
# -----------------------------

@app.post("/download")
def download_pdf(data: Question):
    os.makedirs("downloads", exist_ok=True)
    filename = "downloads/AI_StudyMate_Notes.pdf"

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    story = [
        Paragraph("<b>AI StudyMate Notes</b>", styles["Heading1"]),
        Paragraph(data.question.replace("\n", "<br/>"), styles["BodyText"]),
    ]

    doc.build(story)

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename="Ai_study_notes.pdf"
    )
    return{
        "message":"PDF created sucessfully",
        "file":filename
    }


# -----------------------------
# Quiz Generator
# -----------------------------

# -----------------------------
# Quiz Generator
# -----------------------------

@app.get("/quiz")
def generate_quiz():

    global pdf_text

    if pdf_text == "":
        return {
            "quiz": "Please upload a PDF first."
        }


    prompt = f"""
You are an experienced university professor.

Create a quiz from this study material.

Generate 10 MCQ questions.

Format:

## Question 1

Question:

A)
B)
C)
D)

Correct Answer:

Explanation:


Study Material:

{pdf_text[:15000]}
"""


    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        return {
            "quiz": response.text
        }

    except Exception as e:
        return {
            "quiz": "Error generating quiz",
            "details": str(e)
        }
# -----------------------------
# Health Check
# -----------------------------

@app.get("/status")
def status():
    return {
        "status": "Running",
        "application": "AI StudyMate",
        "pdf_uploaded": pdf_text != "",
        "characters_loaded": len(pdf_text),
    }

    