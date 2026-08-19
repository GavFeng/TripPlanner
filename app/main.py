from fastapi import FastAPI

app = FastAPI(title="Trip Planner API")


@app.get("/")
def root():
    return {"message": "Trip Planner API is running"}