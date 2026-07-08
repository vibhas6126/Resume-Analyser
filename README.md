# ResumeIQ

ResumeIQ is an AI-powered resume analyzer built with FastAPI, SQLAlchemy, and React.

## Backend quick start

1. Create and activate a virtual environment:
   - `python -m venv venv`
   - `venv\Scripts\Activate.ps1`
2. Install dependencies:
   - `pip install -r backend/requirements.txt`
3. Copy the environment template:
   - `Copy-Item backend/.env.example backend/.env`
4. Update the values in `backend/.env` for your local MySQL instance.
5. Start the API:
   - `uvicorn app.main:app --reload --app-dir backend`

## Notes

- The backend uses SQLAlchemy and Alembic for persistence.
- Resume uploads are stored under `backend/uploads/`.
- Authentication uses JWT and password hashing.
