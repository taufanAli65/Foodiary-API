import requests
import time
import os
from fastapi import FastAPI, Query
from dotenv import load_dotenv

# Load variabel dari file .env
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
BASE_URL = "https://platform.fatsecret.com/rest/server.api"

app = FastAPI()

# Menyimpan token OAuth2 secara global agar tidak perlu request ulang setiap kali
access_token = None
token_expiry = 0  # Waktu kedaluwarsa token


def get_access_token():
    """Mengambil token OAuth2 dari FatSecret"""
    global access_token, token_expiry

    # Jika token masih berlaku, gunakan token yang ada
    if access_token and time.time() < token_expiry:
        return access_token

    # Request token baru jika belum ada atau sudah expired
    response = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code == 200:
        data = response.json()
        access_token = data["access_token"]
        token_expiry = time.time() + data["expires_in"] - 60  # Tambahkan buffer 60 detik
        return access_token
    else:
        raise Exception(f"Error mendapatkan token: {response.text}")


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
        return response.json()
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
        return response.json()
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
        return {"error": "Gagal mencari makanan"}

    search_data = search_response.json()

    # Pastikan ada hasil pencarian
    foods = search_data.get("foods", {}).get("food", [])
    if not foods:
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
        return {"error": "Gagal mengambil data nutrisi"}

    nutrition_data = nutrition_response.json()

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
        return response.json()
    return {"error": "Gagal mengambil data makanan"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
