poetry run uvicorn src.api:app --host=0.0.0.0  --port=5000

poetry run python schedule_tracking.py