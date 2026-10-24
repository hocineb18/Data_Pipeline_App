"""Collecte des avis Trustpilot : extraction des avis depuis le JSON intégré aux pages."""
import json
from bs4 import BeautifulSoup


def clean_review(review):
    """Transforme un avis brut de Trustpilot en dictionnaire plat ne contenant que les champs retenus."""
    verification = (review.get("labels") or {}).get("verification") or {}
    consumer = review.get("consumer") or {}
    return {
        "review_id": review["id"],
        "title": review.get("title"),
        "text": review.get("text"),
        "rating": review.get("rating"),
        "published_date": (review.get("dates") or {}).get("publishedDate"),
        "author": consumer.get("displayName"),
        "country": consumer.get("countryCode"),
        "language": review.get("language"),
        "verification_level": verification.get("verificationLevel"),
        "has_reply": review.get("reply") is not None,
        "likes": review.get("likes", 0),
    }


def extract_reviews(html):
    """Extrait les avis du bloc JSON __NEXT_DATA__ d'une page Trustpilot ; renvoie une liste vide si le bloc est absent."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if script is None:
        return []
    raw_reviews = json.loads(script.string)["props"]["pageProps"]["reviews"]
    return [clean_review(review) for review in raw_reviews]


if __name__ == "__main__":
    with open("data/raw/page_test.html", encoding="utf-8") as file:
        reviews = extract_reviews(file.read())
    print(f"{len(reviews)} avis extraits")
    print(reviews[0])
