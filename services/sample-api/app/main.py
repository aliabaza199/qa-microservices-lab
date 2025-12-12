from fastapi import FastAPI

app = FastAPI(title="sample-api")

@app.get("/health")
def health():
    return {"status":"ok"}
