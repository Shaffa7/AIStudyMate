






    from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
import shutil
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Load environment variables
load_dotenv()

# Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# FastAPI App
app = FastAPI()
pdf_text = ""

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Model
class Question(BaseModel):
    question: str


# Home Route
@app.get("/")
def home():
    return {"message": "AI StudyMate Backend Running"}


# AI Chat Route
@app.post("/chat")
def chat(data: Question):
    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=data.question,
        )

        return {"answer": response.text}

    except Exception as e:
        return {"answer": str(e)}


# PDF Upload Route
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global pdf_text

    os.makedirs("uploads", exist_ok=True)

    path = os.path.join("uploads", file.filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    reader = PdfReader(path)

    pdf_text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pdf_text += page_text

        return {
        "message": "PDF uploaded successfully"
    }


@app.get("/summary")
def summary():

    global pdf_text

    if pdf_text == "":
        return {"summary": "Please upload a PDF first."}

    prompt = f"""
Read the following study material and do the following:

1. Write a short summary.
2. List the important points.
3. Explain in simple language.

Study Material:

{pdf_text[:12000]}
"""

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )

    return {
        "summary": response.text
    }
@app.get("/mcq")
def generate_mcq():

    global pdf_text

    if pdf_text == "":
        return {"mcq": "Please upload a PDF first."}

    prompt = f"""
You are an expert teacher.

Read the study material below and create 10 multiple-choice questions.

Format:

Q1.
A.
B.
C.
D.

Answer:

Study Material:

{pdf_text[:12000]}
"""

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )

    return {
        "mcq": response.text
    }
@app.get("/flashcards")
def flashcards():

    global pdf_text

    if pdf_text == "":
        return {"flashcards": "Please upload a PDF first."}

    prompt = f"""
Create 10 beautiful study flashcards from the following study material.

Rules:
- Use Markdown formatting.
- Each flashcard should have:
  ## Flashcard 1
  **Question:**
  ...
  **Answer:**
  ...

Leave one blank line between flashcards.

Study Material:

{pdf_text[:12000]}
"""

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )

    return {
        "flashcards": response.text
    }  
@app.post("/download")
def download_pdf(data: Question):

    os.makedirs("downloads", exist_ok=True)

    filename = "downloads/AI_StudyMate_Notes.pdf"

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    story = [
        Paragraph("<b>AI StudyMate Notes</b>", styles["Heading1"]),
        Paragraph(data.question.replace("\n", "<br/>"), styles["BodyText"])
    ]

    doc.build(story)

    return {
        "message": "PDF created successfully!",
        "file": filename
    }  
@app.post("/quiz")
async def generate_quiz(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file.file)

    prompt = f"""
    From the following study material, generate a quiz.

    Generate:
    - 10 Multiple Choice Questions
    - Four options (A, B, C, D)
    - Mention the correct answer after each question.

    Study Material:
    {text}
    """

    response = model.generate_content(prompt)

    return {"quiz": response.text}         