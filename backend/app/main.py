from fastapi import FastAPI

app = FastAPI(
    title="ResumeIQ API",
    description="AI Resume Analyzer Backend",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Welcome to ResumeIQ API!"
    }

@app.get("/health")
def health():
    return {
        "status": "Running"
    }