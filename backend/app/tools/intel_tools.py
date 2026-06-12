from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from app.core.database import SessionLocal
from app.models.web_intell_model import WebIntelligenceCache


def scrape_public_sentiment(company_name: str) -> dict:
    db = SessionLocal()

    # 1. Check cache first
    now = datetime.utcnow()
    cached = db.query(WebIntelligenceCache).filter(
        WebIntelligenceCache.target_entity == company_name,
        WebIntelligenceCache.expires_at > now
    ).first()

    if cached:
        return {
            "source": "cache",
            "data": cached.scraped_data
        }

    # 2. Real scrape with fallback
    scraped_data = _scrape_g2_reviews(company_name)

    if not scraped_data:
        scraped_data = _scrape_trustpilot_reviews(company_name)

    if not scraped_data:
        scraped_data = _generate_fallback_intelligence(company_name)

    # 3. Save to cache (6 hour expiry)
    new_cache = WebIntelligenceCache(
        source_url=f"https://www.g2.com/products/{company_name.lower().replace(' ', '-')}/reviews",
        target_entity=company_name,
        scraped_data=scraped_data,
        scraped_at=now,
        expires_at=now + timedelta(hours=6)
    )

    db.add(new_cache)
    db.commit()

    return {
        "source": "live_scrape",
        "data": scraped_data
    }


def _scrape_g2_reviews(company_name: str) -> dict | None:
    try:
        slug = company_name.lower().replace(" ", "-")
        url = f"https://www.g2.com/products/{slug}/reviews"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SenAI-Intelligence-Bot/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        rating_elem = soup.select_one("[data-g2-review-rating]")
        rating = float(rating_elem.get("data-g2-review-rating", 0)) if rating_elem else 0

        review_elems = soup.select(".review")
        reviews = []
        for elem in review_elems[:5]:
            title = elem.select_one(".review-title")
            body = elem.select_one(".review-body")
            if title or body:
                reviews.append({
                    "title": title.get_text(strip=True) if title else "",
                    "body": body.get_text(strip=True) if body else ""
                })

        themes = _extract_themes(reviews)

        return {
            "platform": "G2",
            "current_rating": rating,
            "recent_reviews": len(reviews),
            "themes": themes,
            "sentiment_status": _calculate_sentiment_status(rating, themes)
        }
    except Exception:
        return None


def _scrape_trustpilot_reviews(company_name: str) -> dict | None:
    try:
        slug = company_name.lower().replace(" ", "")
        url = f"https://www.trustpilot.com/review/{slug}.com"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SenAI-Intelligence-Bot/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        rating_elem = soup.select_one("[data-rating]")
        rating = float(rating_elem.get("data-rating", 0)) if rating_elem else 0

        review_elems = soup.select(".review-card")
        reviews = []
        for elem in review_elems[:5]:
            title = elem.select_one(".review-title")
            body = elem.select_one(".review-body")
            if title or body:
                reviews.append({
                    "title": title.get_text(strip=True) if title else "",
                    "body": body.get_text(strip=True) if body else ""
                })

        themes = _extract_themes(reviews)

        return {
            "platform": "Trustpilot",
            "current_rating": rating,
            "recent_reviews": len(reviews),
            "themes": themes,
            "sentiment_status": _calculate_sentiment_status(rating, themes)
        }
    except Exception:
        return None


def _extract_themes(reviews: list[dict]) -> list[str]:
    negative_keywords = [
        "slow", "lag", "bug", "crash", "down", "outage", "support", "issue",
        "problem", "error", "fail", "broken", "bad", "worst", "terrible"
    ]
    positive_keywords = [
        "great", "excellent", "love", "amazing", "best", "awesome", "good",
        "helpful", "fast", "reliable", "easy", "perfect"
    ]

    themes = []
    for review in reviews:
        text = f"{review.get('title', '')} {review.get('body', '')}".lower()
        for keyword in negative_keywords:
            if keyword in text and f"Support: {keyword}" not in themes:
                themes.append(f"Support: {keyword}")
        for keyword in positive_keywords:
            if keyword in text and f"Feature: {keyword}" not in themes:
                themes.append(f"Feature: {keyword}")

    return themes[:5]


def _calculate_sentiment_status(rating: float, themes: list[str]) -> str:
    negative_count = sum(1 for t in themes if t.startswith("Support:"))
    if rating < 3.0 or negative_count >= 3:
        return "deteriorating"
    if rating < 3.5 or negative_count >= 2:
        return "declining"
    if rating >= 4.0 and negative_count == 0:
        return "healthy"
    return "stable"


def _generate_fallback_intelligence(company_name: str) -> dict:
    return {
        "platform": "fallback",
        "current_rating": 0,
        "recent_reviews": 0,
        "themes": ["No live data available"],
        "sentiment_status": "unknown",
        "note": "Live scraping failed. Check network connectivity or robots.txt compliance."
    }
