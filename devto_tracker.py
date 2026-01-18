#!/usr/bin/env python3
import os
import requests
import json
import argparse
from datetime import datetime, timezone
from dotenv import load_dotenv
from core.database import DatabaseManager
from core.content_tracker import ContentTracker

load_dotenv()

class DevToTracker:
    def __init__(self, api_key, db_path="devto_metrics.db"):
        self.api_key = api_key
        self.headers = {"api-key": api_key}
        self.db = DatabaseManager(db_path)
        self.content_tracker = ContentTracker(db_path)

    def fetch_api_articles(self):
        """Récupération brute depuis l'API Dev.to."""
        url = "https://dev.to/api/articles/me/all"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def collect_snapshot(self):
        """Action principale : Métriques + Tracking de contenu."""
        articles = self.fetch_api_articles()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        print(f"📡 Start collection: {len(articles)} articles found.")
        
        with self.db.get_connection() as conn:
            for art in articles:
                # 1. Insertion du Snapshot (article_metrics)
                conn.execute("""
                    INSERT INTO article_metrics 
                    (collected_at, article_id, title, slug, published_at, views, reactions, comments, reading_time_minutes, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp, art['id'], art['title'], art['slug'], 
                    art['published_at'], art['page_views_count'], 
                    art['public_reactions_count'], art['comments_count'],
                    art['reading_time_minutes'], json.dumps(art['tag_list'])
                ))

                # 2. Tracking automatique des modifications (Titre, etc.)
                self.content_tracker.track_changes(
                    article_id=art['id'],
                    current_title=art['title'],
                    current_tags=json.dumps(art['tag_list']),
                    edited_at_api=art.get('edited_at') # Utilisation du champ API
                )
            
            conn.commit()
        print(f"✅ Data stored and content checked.")

def main():
    parser = argparse.ArgumentParser(description='Dev.to Tracker - Refactored Edition')
    parser.add_argument('--collect', action='store_true', help='Collect metrics and track changes')
    args = parser.parse_args()

    api_key = os.getenv('DEVTO_API_KEY')
    if not api_key:
        print("❌ Error: DEVTO_API_KEY environment variable not set.")
        return

    tracker = DevToTracker(api_key)
    if args.collect:
        tracker.collect_snapshot()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()