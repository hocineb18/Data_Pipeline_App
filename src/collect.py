"""Collecte des avis Trustpilot : navigation avec Playwright et extraction du JSON intégré aux pages."""
import json
import random
import time

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

BASE_URL = "https://fr.trustpilot.com/review/boursobank.com"
CHALLENGE_TITLE = "Verifying Connection"
OUTPUT_CSV = "data/raw/reviews_boursobank.csv"


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


def load_page(page, url):
    """Charge une URL dans l'onglet Playwright, attend la fin de la vérification anti-robot et renvoie le HTML."""
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    try:
        page.wait_for_function(f"document.title !== '{CHALLENGE_TITLE}'", timeout=30000)
        page.wait_for_load_state("domcontentloaded")
    except PlaywrightTimeoutError:
        print(f"Vérification non passée pour {url}")
    return page.content()


def scrape_reviews(base_url, max_pages, min_delay=2, max_delay=5):
    """Parcourt les pages d'avis de 1 à max_pages et renvoie tous les avis ; s'arrête dès qu'une page est vide."""
    all_reviews = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page(locale="fr-FR")
        for page_number in range(1, max_pages + 1):
            url = f"{base_url}?page={page_number}"
            reviews = extract_reviews(load_page(page, url))
            if not reviews:
                print(f"Page {page_number} : aucun avis, arrêt de la collecte.")
                break
            all_reviews.extend(reviews)
            print(f"Page {page_number} : {len(reviews)} avis (total : {len(all_reviews)})")
            time.sleep(random.uniform(min_delay, max_delay))
        browser.close()
    return all_reviews


def save_to_csv(reviews, path):
    """Enregistre les avis dans un fichier CSV, après suppression des doublons sur review_id."""
    df = pd.DataFrame(reviews).drop_duplicates(subset="review_id")
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"{len(df)} avis enregistrés dans {path}")


if __name__ == "__main__":
    collected_reviews = scrape_reviews(BASE_URL, max_pages=3)
    save_to_csv(collected_reviews, OUTPUT_CSV)
