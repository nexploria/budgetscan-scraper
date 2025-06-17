# BudgetScan Scraper

Application FastAPI qui récupère les produits d'un supermarché (via scraping) et les rend disponibles via API REST.

## Lancer en local
```
pip install -r requirements.txt
python budgetscan_scraper_app.py
```

## Routes
- `GET /produits?supermarche=Super U`
- `POST /scrape?url=https://...&supermarche=Super U`