"""
Trending Data Fetcher
Fetches trending daily products and news respecting quotas
"""
import os
import logging
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
from services.quota_manager import quota_manager

logger = logging.getLogger(__name__)

class TrendingDataFetcher:
    """Fetches trending products and news while respecting free tier quotas"""

    def __init__(self):
        # Don't load API keys in __init__ - they may not be loaded yet
        # Load them lazily when needed
        pass

    def _get_api_keys(self):
        """Get API keys lazily to ensure .env is loaded"""
        return {
            "news_api_key": os.getenv("NEWS_API_KEY", "").strip(),
            "gemini_api_key": os.getenv("GOOGLE_API_KEY", "").strip()
        }

    def fetch_trending_products(self) -> List[str]:
        """
        Fetch trending daily products from NewsAPI
        Returns: List of product names in trend
        """
        keys = self._get_api_keys()
        news_api_key = keys["news_api_key"]

        if not quota_manager.can_use("newsapi"):
            logger.warning("[WARN] NewsAPI quota exhausted - skipping product fetch")
            return []

        try:
            # Search for trending consumer products in news
            keywords = [
                "best products 2025",
                "trending gadgets",
                "popular consumer products",
                "must have daily products",
                "new product launches"
            ]

            trending_products = []

            for keyword in keywords:
                if not quota_manager.can_use("newsapi"):
                    break

                params = {
                    "q": keyword,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 10,
                    "apiKey": news_api_key
                }

                response = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
                response.raise_for_status()

                if response.status_code == 200 and quota_manager.consume("newsapi"):
                    data = response.json()
                    articles = data.get("articles", [])

                    # Extract product mentions from titles and descriptions
                    for article in articles:
                        title = article.get("title", "").lower()
                        description = article.get("description", "").lower()
                        content = title + " " + description

                        # Extract product names (simple heuristic)
                        words = content.split()
                        for i, word in enumerate(words):
                            if any(indicator in word for indicator in ["product", "phone", "watch", "tablet", "laptop", "headphone"]):
                                if i > 0:
                                    product = " ".join(words[max(0, i-2):i+1])
                                    if len(product) > 3 and product not in trending_products:
                                        trending_products.append(product)

            logger.info(f"[OK] Fetched {len(trending_products)} trending products")
            return trending_products[:10]  # Top 10

        except Exception as e:
            logger.error(f"[FAIL] Error fetching trending products: {e}")
            return []

    def fetch_trending_news(self, products: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch trending news for each product
        Returns: {product: [articles]}
        """
        keys = self._get_api_keys()
        news_api_key = keys["news_api_key"]

        news_by_product = {}

        for product in products:
            if not quota_manager.can_use("newsapi"):
                logger.warning("[WARN] NewsAPI quota exhausted - stopping news fetch")
                break

            try:
                params = {
                    "q": product,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 15,
                    "apiKey": news_api_key
                }

                response = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)

                if response.status_code == 200 and quota_manager.consume("newsapi"):
                    data = response.json()
                    articles = data.get("articles", [])

                    news_by_product[product] = [
                        {
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "url": article.get("url", ""),
                            "source": article.get("source", {}).get("name", ""),
                            "published_at": article.get("publishedAt", ""),
                            "content": article.get("content", "")
                        }
                        for article in articles[:5]  # Top 5 per product
                    ]

                    logger.info(f"[OK] Fetched {len(news_by_product[product])} articles for {product}")

            except Exception as e:
                logger.error(f"[FAIL] Error fetching news for {product}: {e}")
                continue

        return news_by_product

    def get_quota_status(self) -> Dict[str, Any]:
        """Get current quota status"""
        return {
            "newsapi": quota_manager.get_status("newsapi"),
            "gemini": quota_manager.get_status("gemini"),
            "timestamp": datetime.now().isoformat()
        }


# Global instance
trending_fetcher = TrendingDataFetcher()
