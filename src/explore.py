"""Exploration : première requête vers une page d'avis Trustpilot, via un vrai navigateur (Playwright)."""
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

URL = "https://fr.trustpilot.com/review/boursobank.com"
CHALLENGE_TITLE = "Verifying Connection"


def fetch_page(url):
    """Ouvre la page dans Chromium, attend la fin de la vérification anti-robot et renvoie le HTML."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page(locale="fr-FR")
        response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
        print("Code HTTP initial :", response.status)
        try:
            page.wait_for_function(
                f"document.title !== '{CHALLENGE_TITLE}'", timeout=30000
            )
            page.wait_for_load_state("domcontentloaded")
            print("Vérification passée.")
        except PlaywrightTimeoutError:
            print("La vérification n'a pas abouti en 30 secondes.")
        html = page.content()
        browser.close()
    return html


if __name__ == "__main__":
    html = fetch_page(URL)
    with open("data/raw/page_test.html", "w", encoding="utf-8") as file:
        file.write(html)
    soup = BeautifulSoup(html, "html.parser")
    print("Titre de la page :", soup.title.string)
    print("Données JSON intégrées :", soup.find("script", id="__NEXT_DATA__") is not None)
