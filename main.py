import os
import logging
import time
import base64
from fastapi import FastAPI, Query, UploadFile, File
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
BASE_URL = "https://platform.fatsecret.com/rest/server.api"
IMAGE_RECOGNITION_URL = "https://platform.fatsecret.com/rest/image-recognition/v1"

# Initialize FastAPI
app = FastAPI()

# Global variables to store token and expiration time
access_token = None
token_expiry = 0  # Token expiry timestamp

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_access_token():
    """Get OAuth2 access token"""
    global access_token, token_expiry

    # If the token is still valid, use the cached one
    if access_token and time.time() < token_expiry:
        return access_token

    # Request a new token if not present or expired
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",  # client_credentials flow
            # Remove the incorrect scope
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code == 200:
        data = response.json()
        access_token = data["access_token"]
        token_expiry = time.time() + data["expires_in"] - 60  # Buffer 60 seconds
        return access_token
    else:
        logging.error(f"Error getting token: {response.text}")
        raise Exception(f"Error getting token: {response.text}")

@app.get("/search_food")
def search_food(query: str = Query(..., description="Nama makanan yang ingin dicari")):
    """Mencari makanan berdasarkan kata kunci"""
    token = get_access_token()

    params = {
        "method": "foods.search",
        "format": "json",
        "search_expression": query,
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(BASE_URL, params=params, headers=headers)
    
    if response.status_code == 200:
        logging.info(f"search_food response: {response.json()}")
        return response.json()
    logging.error(f"search_food error: {response.text}")
    return {"error": "Gagal mengambil data dari FatSecret API"}

@app.get("/food_nutrition")
def get_food_nutrition(food_id: str = Query(..., description="ID makanan dari FatSecret")):
    """Mendapatkan informasi nutrisi berdasarkan food_id"""
    token = get_access_token()

    params = {
        "method": "food.get",
        "format": "json",
        "food_id": food_id,
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(BASE_URL, params=params, headers=headers)
    
    if response.status_code == 200:
        logging.info(f"get_food_nutrition response: {response.json()}")
        return response.json()
    logging.error(f"get_food_nutrition error: {response.text}")
    return {"error": "Gagal mengambil data nutrisi"}

@app.get("/search_food_detail")
def search_food_detail(query: str = Query(..., description="Nama makanan yang ingin dicari")):
    """Mencari makanan berdasarkan nama dan langsung mengambil detail nutrisinya"""
    token = get_access_token()

    # Step 1: Cari makanan berdasarkan nama
    search_params = {
        "method": "foods.search",
        "format": "json",
        "search_expression": query,
    }

    headers = {"Authorization": f"Bearer {token}"}
    search_response = requests.get(BASE_URL, params=search_params, headers=headers)

    if search_response.status_code != 200:
        logging.error(f"search_food_detail search error: {search_response.text}")
        return {"error": "Gagal mencari makanan"}

    search_data = search_response.json()

    # Pastikan ada hasil pencarian
    foods = search_data.get("foods", {}).get("food", [])
    if not foods:
        logging.info("search_food_detail: Makanan tidak ditemukan")
        return {"error": "Makanan tidak ditemukan"}

    # Ambil food_id dari hasil pertama
    if isinstance(foods, list):
        food_id = foods[0]["food_id"]
    else:
        food_id = foods["food_id"]

    # Step 2: Ambil detail nutrisi berdasarkan food_id
    nutrition_params = {
        "method": "food.get",
        "format": "json",
        "food_id": food_id,
    }

    nutrition_response = requests.get(BASE_URL, params=nutrition_params, headers=headers)

    if nutrition_response.status_code != 200:
        logging.error(f"search_food_detail nutrition error: {nutrition_response.text}")
        return {"error": "Gagal mengambil data nutrisi"}

    nutrition_data = nutrition_response.json()
    logging.info(f"search_food_detail response: {nutrition_data}")

    return nutrition_data

@app.get("/search_food_by_id")
def search_food_by_id(food_id: str = Query(..., description="ID makanan dari FatSecret")):
    """Mencari makanan berdasarkan food_id dan mengambil detail nutrisinya"""
    token = get_access_token()

    params = {
        "method": "food.get",
        "format": "json",
        "food_id": food_id,
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(BASE_URL, params=params, headers=headers)
    
    if response.status_code == 200:
        logging.info(f"search_food_by_id response: {response.json()}")
        return response.json()
    logging.error(f"search_food_by_id error: {response.text}")
    return {"error": "Gagal mengambil data makanan"}

@app.post("/scan")
async def scan_food(image: UploadFile = File(...)):
    """Scan food image and return detected foods"""
    token = get_access_token()

    # Read image file and encode it to base64
    image_bytes = await image.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "image_b64": image_b64,
        "region": "US",
        "language": "en",
        "include_food_data": True,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(IMAGE_RECOGNITION_URL, json=payload, headers=headers)

    if response.status_code == 200:
        logging.info(f"scan_food response: {response.json()}")
        return response.json()
    elif response.status_code == 403 and response.json().get('error', {}).get('code') == '21':
        logging.error(f"scan_food error: {response.text}")
        return {"error": "Invalid IP address detected. Please check your API credentials and IP whitelist."}
    else:
        logging.error(f"scan_food error: {response.text}")
        return {"error": "Gagal memindai gambar makanan"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
