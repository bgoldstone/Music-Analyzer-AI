from contextlib import asynccontextmanager
import pathlib
import sys
import dotenv
from fastapi import FastAPI
from pymongo import MongoClient
import uvicorn

# FastAPI routes
from user_routes import user_router
from playlist_routes import playlist_router
from track_routes import track_router

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from database.load_data import MONGO_URL

# Load environment variables
CONFIG = dotenv.dotenv_values("database/.env")

# Connect to the MongoDB database
uri = f"mongodb+srv://{CONFIG.get('MONGO_USER')}:{CONFIG.get('MONGO_PASSWORD')}@{MONGO_URL}/"
mongodb_client = MongoClient(uri)


# Handles startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):

    # handles shutdown events
    yield
    mongodb_client.close()
    print("Disconnected from the MongoDB database!")


app = FastAPI(lifespan=lifespan)

app.database = mongodb_client["soundsmith"]
# TODO add authentication.
app.include_router(user_router)
app.include_router(playlist_router)
app.include_router(track_router)
print("Connected to the MongoDB database!")
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=f'{CONFIG.get("API_HOST")}',
        port=f'{int(CONFIG.get("API_PORT"))}',
    )
