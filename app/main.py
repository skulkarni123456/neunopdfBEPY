from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# disable docs ui
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# minimal CORS to allow your frontend; change origin if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
from app.routers.pdf_router import router as pdf_router
from app.routers.convert_router import router as convert_router
from app.routers.image_router import router as image_router
from app.routers.security_router import router as security_router

app.include_router(pdf_router, prefix="/pdf")
app.include_router(convert_router, prefix="/convert")
app.include_router(image_router, prefix="/convert")
app.include_router(security_router, prefix="/security")

# health
@app.get("/health")
async def health():
    return {"status": "ok"}
