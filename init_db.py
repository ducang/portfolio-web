import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:

        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                year INTEGER,
                venue TEXT,
                summary TEXT
            );
        """)

        cur.execute("""
            INSERT INTO projects (
                title,
                slug,
                year,
                venue,
                summary
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (slug) DO NOTHING;
        """, (
            "VETI: 3D-Guided Visual Effect Tuning",
            "veti",
            2026,
            "SIGGRAPH Asia 2026 Poster",
            "A geometry-aware image editing pipeline."
        ))

    conn.commit()

print("Database initialized.")