from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Enable CORS for all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to your pre-generated tiles
TILE_DIR = os.path.join(os.getcwd(), "tiles")

#TODO: Add way to collect initial satellite imagery

@app.get("/tiles/{dam_id}/{year}/{month}/{z}/{x}/{y}.png")
async def serve_tile(dam_id: str, year: int, month: int, z: int, x: int, y: int):
    """Serves tiles from the tile directory."""
    tile_path = os.path.join(TILE_DIR, dam_id, str(year), str(month), str(z), str(x), f"{y}.png")

    if os.path.exists(tile_path):
        return FileResponse(tile_path)
    else:
        raise HTTPException(status_code=404, detail="Tile Not Found")


# Run the application with Uvicorn (recommended for FastAPI)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")
