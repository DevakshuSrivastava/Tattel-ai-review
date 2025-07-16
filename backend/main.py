from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import uvicorn
import requests
from docx import Document
from PyPDF2 import PdfReader
import tempfile

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEEPSEEK_API_KEY = "sk-c280139fc10443a5a9cd6045798697c4"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def extract_text(file: UploadFile):
    ext = file.filename.split('.')[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix='.'+ext) as tmp:
        tmp.write(file.file.read())
        tmp.flush()
        if ext == 'pdf':
            reader = PdfReader(tmp.name)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext in ['doc', 'docx']:
            doc = Document(tmp.name)
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            text = ""
    return text

def get_deepseek_score(cv_text):
    prompt = (
        "Review the following CV and provide a score out of 100, along with 2-3 improvement suggestions. "
        "Scoring rules: If the CV is not ready for job applications, score between 40-60. If the CV is well written and describes the candidate clearly for a recruiter, score above 80. "
        "Do not use asterisks (*) in your suggestions. Format suggestions as plain text or numbered list.\n\nCV:\n" + cv_text
    )
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        # Simple parsing: expects "Score: xx" and suggestions as list
        import re
        score_match = re.search(r"Score\s*[:\-]?\s*(\d{1,3})", content)
        score = int(score_match.group(1)) if score_match else None
        suggestions = re.findall(r"(?:Suggestion[s]?|Improvement[s]?|\d+\.)\s*[:\-]?\s*(.*)", content)
        if not suggestions:
            # fallback: split lines after score
            suggestions = [line.strip() for line in content.splitlines() if line.strip() and "Score" not in line]
        return {"score": score, "suggestions": suggestions}
    else:
        return {"score": None, "suggestions": ["Error connecting to DeepSeek API."]}

@app.post("/review-cv")
async def review_cv(file: UploadFile = File(...)):
    text = extract_text(file)
    if not text:
        return JSONResponse({"score": None, "suggestions": ["Could not extract text from CV."]})
    result = get_deepseek_score(text)
    return JSONResponse(result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
