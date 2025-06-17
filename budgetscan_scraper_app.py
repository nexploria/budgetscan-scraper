import requests
from bs4 import BeautifulSoup
import json
import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import schedule
import time
import threading

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def scraper_supermarche(url, nom_supermarche):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    produits = []
    for article in soup.select('.product-item'):
        try:
            nom = article.select_one('.product-title').text.strip()
            prix = article.select_one('.price').text.strip().replace("€", "").replace(",", ".")
            image = article.select_one('img')['src']
            produits.append({
                "nom": nom,
                "prix": float(prix),
                "image_url": image,
                "supermarche": nom_supermarche
            })
        except Exception:
            continue
    with open(f"{DATA_FOLDER}/produits_{nom_supermarche.lower().replace(' ', '')}.json", "w", encoding='utf-8') as f:
        json.dump(produits, f, indent=2, ensure_ascii=False)

@app.get("/produits")
def get_produits(supermarche: str = Query(..., description="Nom du supermarché (ex: Super U)")):
    filepath = f"{DATA_FOLDER}/produits_{supermarche.lower().replace(' ', '')}.json"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding='utf-8') as f:
            return json.load(f)
    return {"error": "Aucune donnée trouvée pour ce supermarché."}

@app.post("/scrape")
def scrape_url(url: str = Query(...), supermarche: str = Query(...)):
    try:
        scraper_supermarche(url, supermarche)
        return {"success": f"Scraping terminé pour {supermarche}"}
    except Exception as e:
        return {"error": str(e)}

def planification_scraping():
    schedule.every().day.at("04:00").do(lambda: scraper_supermarche("https://www.coursesu.com/drive-superu-aimargues", "Super U"))
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=planification_scraping, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run("budgetscan_scraper_app:app", host="0.0.0.0", port=8000, reload=True)