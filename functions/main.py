from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.passport_route import router as passport_router
from routes.identify_route import router as identify_route

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
app.include_router(identify_route)
@app.get("/")
def home():
    return {"status": "passport OCR API running"}