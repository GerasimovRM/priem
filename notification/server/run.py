from api.server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=5000, log_level="info", reload=True)

