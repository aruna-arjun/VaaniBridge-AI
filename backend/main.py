
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from google import genai


# ==================================================
# PROJECT PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv(BASE_DIR / ".env")

gemini_api_key = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

if not gemini_api_key:
    print("WARNING: GEMINI_API_KEY is not configured.")

client = (
    genai.Client(api_key=gemini_api_key)
    if gemini_api_key
    else None
)


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="VaaniBridge AI",
    description="Marathi Voice AI Question Answering Platform",
    version="2.0.0"
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# FRONTEND ROUTE
# ==================================================

@app.get("/")
async def home():

    frontend_file = FRONTEND_DIR / "index.html"

    if not frontend_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Frontend index.html not found."
        )

    return FileResponse(frontend_file)


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/api/health")
async def health_check():

    return {
        "success": True,
        "message": "VaaniBridge AI Gemini backend is running."
    }


# ==================================================
# MARATHI VOICE QUESTION ANSWERING
# ==================================================

@app.post("/api/translate")
async def translate_audio(
    file: UploadFile = File(...)
):

    if client is None:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in backend/.env"
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Audio file is missing."
        )

    temporary_file_path = None
    uploaded_gemini_file = None

    try:

        # ------------------------------------------
        # SAVE AUDIO FILE
        # ------------------------------------------

        audio_content = await file.read()

        if not audio_content:
            raise HTTPException(
                status_code=400,
                detail="Audio file is empty."
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".webm"
        ) as temporary_file:

            temporary_file.write(audio_content)
            temporary_file_path = temporary_file.name

        # ------------------------------------------
        # UPLOAD AUDIO TO GEMINI
        # ------------------------------------------

        uploaded_gemini_file = client.files.upload(
            file=temporary_file_path
        )

        # ------------------------------------------
        # TRANSCRIBE MARATHI AUDIO
        # ------------------------------------------

        transcription_prompt = """
Listen carefully to the attached audio.

The speaker is speaking Marathi.

Write an accurate transcript of everything the speaker says
in Marathi Devanagari script.

Do not answer the question.
Do not translate the question.
Return only the Marathi transcript.
"""

        transcription_response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                uploaded_gemini_file,
                transcription_prompt
            ]
        )

        marathi_text = (
            transcription_response.text or ""
        ).strip()

        if not marathi_text:
            raise HTTPException(
                status_code=400,
                detail="Could not understand the Marathi audio."
            )

        # ------------------------------------------
        # ANSWER THE MARATHI QUESTION IN ENGLISH
        # ------------------------------------------

        answer_prompt = f"""
You are VaaniBridge AI, a helpful general-purpose AI assistant.

The user asked the following question in Marathi:

{marathi_text}

Your task:

1. Understand the actual meaning of the Marathi question.
2. Answer the question, not just translate it.
3. Write the answer in clear, natural English.
4. Handle different types of questions, including:
   - General knowledge
   - Education
   - Science
   - Mathematics
   - History
   - Geography
   - Technology
   - Programming and coding
   - Artificial intelligence
   - Career guidance
   - Daily-life questions
   - Creative questions
   - Problem-solving
5. Explain your answer clearly.
6. Show steps for mathematics when useful.
7. Provide code examples for coding questions when appropriate.
8. If the question is unclear, ask for clarification in English.
9. Do not invent facts.
10. Be honest when information is uncertain.
11. Use simple English when possible.

Return only the English answer.
"""

        answer_response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=answer_prompt
        )

        english_text = (
            answer_response.text or ""
        ).strip()

        if not english_text:
            raise HTTPException(
                status_code=500,
                detail="Gemini did not generate an answer."
            )

        # ------------------------------------------
        # RETURN RESPONSE TO FRONTEND
        # ------------------------------------------

        return {
            "success": True,
            "marathi_text": marathi_text,
            "english_text": english_text,
            "translation": english_text
        }

    except HTTPException:
        raise

    except Exception as error:

        print("ERROR:", str(error))

        raise HTTPException(
            status_code=500,
            detail=f"Gemini processing failed: {str(error)}"
        )

    finally:

        # ------------------------------------------
        # DELETE LOCAL TEMPORARY AUDIO
        # ------------------------------------------

        if temporary_file_path:

            temporary_path = Path(temporary_file_path)

            if temporary_path.exists():
                temporary_path.unlink()

        # ------------------------------------------
        # DELETE GEMINI UPLOADED FILE
        # ------------------------------------------

        if uploaded_gemini_file:

            try:
                client.files.delete(
                    name=uploaded_gemini_file.name
                )

            except Exception as cleanup_error:

                print(
                    "Gemini file cleanup warning:",
                    str(cleanup_error)
                )


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )