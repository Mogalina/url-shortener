import os
import uvicorn
from typing import Dict
from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
SERVER_HOST: str | None = os.getenv('SERVER_HOST')
SERVER_PORT: int | None = int(os.getenv('SERVER_PORT'))

# Initialize API service interface
app: FastAPI = FastAPI()

@app.get("/")
def root() -> Dict[str, str]:
    """
    Returns a message indicating whether the server is up and running.
    
    :return: Message indicating that the server is healthy.
    :rtype: Dict[str, str]
    """
    return {"message": "URL shortener service running."}

@app.post("/url")
async def create_short_url(url: str) -> Dict[str, str]:
    """
    Generates a short alias for the requested URL address.
    
    :param url: The requested URL for transformation.
    :type url: str
    :return: The short and unique alias for the requested URL.
    :rtype: Dict[str, str]
    """
    return {"short_url": url}

if __name__ == "__main__":
    try:
        uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT) 
        print(f"Server running on {SERVER_HOST}:{SERVER_PORT}")
    except Exception as e:
        print("Error running server:", e)
