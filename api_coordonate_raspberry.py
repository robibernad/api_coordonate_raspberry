from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import matplotlib.pyplot as plt
import numpy as np
import base64

app = FastAPI()

# 🔵 Variabile globale
last_coordinates = {
    "x_sonda": 0,
    "y_sonda": 0,
    "z_masurat": 0,
    "magnet_length": 30,
    "magnet_width": 20,
    "magnet_height": 5,
    "progress": 0
}

# 🔵 Model coordonate primite
class Coordinates(BaseModel):
    x_sonda: float
    y_sonda: float
    z_masurat: float
    magnet_length: float
    magnet_width: float
    magnet_height: float
    progress: float

# 🔵 POST pentru update coordonate (Raspberry Pi)
@app.post("/update-coordinates/")
async def update_coordinates(coords: Coordinates):
    global last_coordinates
    last_coordinates = coords.dict()
    return {"message": "Coordinates updated successfully"}

# 🔵 GET pentru a obține ultimele coordonate
@app.get("/get-latest-coordinates/")
async def get_latest_coordinates():
    return last_coordinates

# 🔵 POST pentru generarea imaginii
@app.post("/genereaza-imagine/")
async def genereaza_imagine(coords: Coordinates):
    try:
        x_sonda = coords.x_sonda
        y_sonda = coords.y_sonda
        z_masurat = coords.z_masurat
        magnet_length = coords.magnet_length
        magnet_width = coords.magnet_width
        magnet_height = coords.magnet_height

        z_sonda = magnet_height + z_masurat

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Magnet
        ax.bar3d(0, 0, 0, magnet_length, magnet_width, magnet_height, color='blue', alpha=0.3, shade=True)
        ax.plot([0, magnet_length], [0, 0], [magnet_height, magnet_height], color='black', linestyle='--', linewidth=2)
        ax.text(magnet_length/2, -3, magnet_height + 0.5, "Suprafață Magnet", color='black', fontsize=12)

        # Sonda
        ax.scatter(x_sonda, y_sonda, z_sonda, color='red', s=150)
        ax.plot([x_sonda, x_sonda], [y_sonda, y_sonda], [z_sonda, magnet_height], color='gray', linestyle='--')
        ax.scatter(x_sonda, y_sonda, magnet_height, color='black', s=50, alpha=0.7)

        ax.set_xlim(0, magnet_length)
        ax.set_ylim(0, magnet_width)
        ax.set_zlim(0, magnet_height + 30)
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Distanță (mm)')

        ax.set_title("Poziția sondei față de magnet")
        ax.view_init(elev=30, azim=45)

        output_file = "sonda_temp.png"
        plt.savefig(output_file)
        plt.close()

        with open(output_file, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')

        return JSONResponse(content={"image_base64": encoded_string})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
