from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.passport_route import router as passport_router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(passport_router)

@app.get("/")
def home():
    return {"status": "passport OCR API running"}