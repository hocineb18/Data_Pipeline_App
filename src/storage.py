"""Stockage des avis dans une base SQLite : création du schéma et insertion incrémentale sans doublons."""
import sqlite3

import pandas as pd

DB_PATH = "data/reviews.db"
CSV_PATH = "data/raw/reviews_boursobank.csv"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL UNIQUE,
    platform  TEXT NOT NULL,
    url       TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id          TEXT PRIMARY KEY,
    source_id          INTEGER NOT NULL REFERENCES sources(source_id),
    title              TEXT,
    text               TEXT,
    rating             INTEGER CHECK (rating BETWEEN 1 AND 5),
    published_date     TEXT,
    author             TEXT,
    country            TEXT,
    language           TEXT,
    verification_level TEXT,
    has_reply          INTEGER,
    likes              INTEGER,
    collected_at       TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_REVIEW = """
INSERT OR IGNORE INTO reviews (
    review_id, source_id, title, text, rating, published_date, author,
    country, language, verification_level, has_reply, likes
) VALUES (
    :review_id, :source_id, :title, :text, :rating, :published_date, :author,
    :country, :language, :verification_level, :has_reply, :likes
)
"""


def get_connection(db_path=DB_PATH):
    """Ouvre une connexion à la base SQLite (créée si absente) et active la vérification des clés étrangères."""
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables(connection):
    """Crée les tables sources et reviews si elles n'existent pas encore."""
    connection.executescript(SCHEMA)


def get_or_create_source(connection, name, platform, url):
    """Renvoie l'identifiant d'une source ; la crée d'abord si elle n'existe pas encore."""
    connection.execute(
        "INSERT OR IGNORE INTO sources (name, platform, url) VALUES (?, ?, ?)",
        (name, platform, url),
    )
    row = connection.execute("SELECT source_id FROM sources WHERE url = ?", (url,)).fetchone()
    return row[0]


def insert_reviews(connection, reviews, source_id):
    """Insère les avis d'une source en ignorant ceux déjà présents ; renvoie le nombre d'avis réellement ajoutés."""
    changes_before = connection.total_changes
    rows = [{**review, "source_id": source_id} for review in reviews]
    connection.executemany(INSERT_REVIEW, rows)
    connection.commit()
    return connection.total_changes - changes_before


def load_reviews_from_csv(csv_path):
    """Lit un CSV d'avis et renvoie une liste de dictionnaires, avec None à la place des valeurs manquantes."""
    df = pd.read_csv(csv_path)
    df = df.astype(object).where(pd.notna(df), None)
    return df.to_dict(orient="records")


if __name__ == "__main__":
    connection = get_connection()
    create_tables(connection)
    source_id = get_or_create_source(
        connection, "BoursoBank", "Trustpilot", "https://fr.trustpilot.com/review/boursobank.com"
    )
    reviews = load_reviews_from_csv(CSV_PATH)
    inserted = insert_reviews(connection, reviews, source_id)
    total = connection.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    print(f"{len(reviews)} avis lus, {inserted} nouveaux insérés, {total} avis au total dans la base.")
    connection.close()
