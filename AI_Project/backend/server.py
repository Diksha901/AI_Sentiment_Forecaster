"""
TrendAI Backend Server
Main FastAPI application with authentication, scraping, and sentiment analysis
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from oauth2 import verify_access_token
from routers import authentication
import sys
from pymongo import MongoClient
import pandas as pd
import time

# Try to import scraping modules (optional)
try:
    from scraper.selenium_scraper import scrape_reviews, get_product_links
    from scraper.news_scraper import scrape_news
    SCRAPING_ENABLED = True
except ImportError as e:
    print(f"⚠️  Scraping modules not available: {e}")
    print("  Install selenium and beautifulsoup4 to enable scraping features")
    SCRAPING_ENABLED = False

# Try to import sentiment engine (optional)
try:
    from llm.sentiment_engine import get_sentiment
    from utils.cleaner import clean_text
    SENTIMENT_ENABLED = True
except ImportError as e:
    print(f"⚠️  Sentiment analysis not available: {e}")
    print("  Install transformers and torch to enable sentiment analysis")
    SENTIMENT_ENABLED = False

# Try to import RAG routes (optional)
try:
    from routers import rag_routes
    RAG_ENABLED = True
except ImportError as e:
    print(f"⚠️  RAG features not available: {e}")
    print("  Install RAG dependencies: pip install -r rag_requirements.txt")
    RAG_ENABLED = False

print("PYTHON PATH:", sys.executable)

# Initialize FastAPI app
app = FastAPI(
    title="TrendAI API",
    description="AI-powered sentiment analysis and market tracking platform",
    version="1.0.0"
)

# CORS Middleware - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication router
app.include_router(authentication.router)

# Include RAG router if available
if RAG_ENABLED:
    app.include_router(rag_routes.router)
    print("✓ RAG routes loaded")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# MongoDB Atlas connection
try:
    client = MongoClient(
        "mongodb+srv://DevanshVerma:qazxsw123@cluster0.fxr8rpr.mongodb.net/ai_project_db?retryWrites=true&w=majority&appName=Cluster0",
        serverSelectionTimeoutMS=5000
    )
    client.server_info()
    print("✓ MongoDB Atlas Connected Successfully")
except Exception as e:
    print("✗ MongoDB Connection Failed:", e)
    print("  Check your internet connection and MongoDB Atlas credentials")

db = client["ai_project_db"]
product_collection = db["product_results"]
news_collection = db["news_results"]


# -----------------------
# Root Endpoint
# -----------------------
@app.get("/")
def read_root():
    return {
        "message": "Welcome to TrendAI API",
        "version": "1.0.0",
        "status": "running"
    }


# -----------------------
# Protected Route Example
# -----------------------
@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    return {"message": "You are authorized", "user": payload}


# -----------------------
# Product Scraping Route
# -----------------------
@app.get("/api/scrape/products")
def run_pipeline():
    """
    Scrape product reviews from Amazon and analyze sentiment
    """
    if not SCRAPING_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Scraping functionality is not available. Install required dependencies."
        )
    
    if not SENTIMENT_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Sentiment analysis is not available. Install required dependencies."
        )
    
    categories = {
        "electronics": "https://www.amazon.in/s?i=electronics",
        "clothes": "https://www.amazon.in/s?i=fashion",
        "essentials": "https://www.amazon.in/s?i=grocery"
    }
   
    all_results = []

    for category_name, category_url in categories.items():
        print(f"Scraping category: {category_name}")

        product_links = get_product_links(category_url)
        product_links = product_links[:3]  # Limit to avoid blocking

        for product_url in product_links:
            try:
                raw_reviews = scrape_reviews(product_url)
                print(f"Reviews found: {len(raw_reviews)}")

                for item in raw_reviews:
                    cleaned = clean_text(item["text"])
                    sentiment = get_sentiment(cleaned)

                    data = {
                        "category": category_name,
                        "product_url": product_url,
                        "review": item["text"],
                        "sentiment_label": sentiment["label"],
                        "confidence_score": sentiment.get("confidence_score", 0),
                        "negative_percent": sentiment.get("percentages", {}).get("Negative", 0),
                        "neutral_percent": sentiment.get("percentages", {}).get("Neutral", 0),
                        "positive_percent": sentiment.get("percentages", {}).get("Positive", 0),
                    }

                    all_results.append(data)
                    product_collection.insert_one(data)

                time.sleep(5)  # Avoid rate limiting

            except Exception as e:
                print(f"Error scraping {product_url}: {e}")
                continue

    return {"message": "Product scraping completed", "count": len(all_results)}


# -----------------------
# News Scraping Route
# -----------------------
@app.get("/api/scrape/news")
def run_news_pipeline():
    """
    Scrape news articles and analyze sentiment
    """
    if not SCRAPING_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Scraping functionality is not available. Install required dependencies."
        )
    
    if not SENTIMENT_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Sentiment analysis is not available. Install required dependencies."
        )
    
    news_data = scrape_news()
    results = []

    for article in news_data:
        combined_text = article["title"] + " " + article["description"]
        cleaned = clean_text(combined_text)
        sentiment = get_sentiment(cleaned)

        data = {
            "platform": "news",
            "keyword": article["keyword"],
            "title": article["title"],
            "description": article["description"],
            "sentiment_label": sentiment["label"],
            "sentiment_score": sentiment.get("confidence_score", 0),
            "published_date": article["published_date"]
        }

        results.append(data)
        news_collection.insert_one(data)

    return {"message": "News scraping completed", "count": len(results)}


# -----------------------
# Get Stored Products
# -----------------------
@app.get("/api/products")
def get_products():
    """
    Retrieve all stored product reviews and sentiments
    """
    data = list(product_collection.find({}, {"_id": 0}).limit(100))
    return {"count": len(data), "data": data}


# -----------------------
# Get Stored News
# -----------------------
@app.get("/api/news")
def get_news():
    """
    Retrieve all stored news articles and sentiments
    """
    data = list(news_collection.find({}, {"_id": 0}).limit(100))
    return {"count": len(data), "data": data}


# -----------------------
# Health Check
# -----------------------
@app.get("/api/health")
def health_check():
    """
    Check if all services are running properly
    """
    mongo_status = "connected"
    try:
        client.server_info()
    except:
        mongo_status = "disconnected"
    
    return {
        "status": "healthy",
        "mongodb": mongo_status,
        "scraping_enabled": SCRAPING_ENABLED,
        "sentiment_enabled": SENTIMENT_ENABLED,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting TrendAI Server...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔗 Server running at: http://localhost:8000\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
