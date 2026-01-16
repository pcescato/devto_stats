#!/usr/bin/env python3
"""
DEV.to Metrics Tracker - Historical data collection
Collecte automatique des métriques pour analyse temporelle
"""

import sqlite3
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional
import json
import argparse

class DevToTracker:
    def __init__(self, api_key: str, db_path: str = "devto_metrics.db"):
        self.api_key = api_key
        self.base_url = "https://dev.to/api"
        self.headers = {"api-key": api_key}
        self.db_path = db_path
        self.conn = None
    
    def connect_db(self):
        """Connect to database for read operations"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            self.conn.row_factory = sqlite3.Row
        
    def init_db(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = self.conn.cursor()
        
        # Table: snapshots globaux
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collected_at TIMESTAMP NOT NULL,
                total_articles INTEGER,
                total_views INTEGER,
                total_reactions INTEGER,
                total_comments INTEGER,
                follower_count INTEGER,
                UNIQUE(collected_at)
            )
        """)
        
        # Table: métriques par article
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS article_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collected_at TIMESTAMP NOT NULL,
                article_id INTEGER NOT NULL,
                title TEXT,
                slug TEXT,
                published_at TIMESTAMP,
                views INTEGER,
                reactions INTEGER,
                comments INTEGER,
                reading_time_minutes INTEGER,
                tags TEXT,
                UNIQUE(collected_at, article_id)
            )
        """)
        
        # Table: événements followers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS follower_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collected_at TIMESTAMP NOT NULL,
                follower_count INTEGER,
                new_followers_since_last INTEGER,
                UNIQUE(collected_at)
            )
        """)
        
        # Table: commentaires
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collected_at TIMESTAMP NOT NULL,
                comment_id TEXT UNIQUE,
                article_id INTEGER,
                article_title TEXT,
                created_at TIMESTAMP,
                author_username TEXT,
                author_name TEXT,
                body_html TEXT,
                body_length INTEGER
            )
        """)
        
        # Table: followers individuels (optionnel, pour tracking détaillé)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS followers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collected_at TIMESTAMP NOT NULL,
                follower_id INTEGER UNIQUE,
                username TEXT,
                name TEXT,
                followed_at TIMESTAMP,
                profile_image TEXT
            )
        """)
        
        # Table: daily analytics (from /api/analytics/historical)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                date DATE NOT NULL,
                page_views INTEGER,
                average_read_time_seconds INTEGER,
                total_read_time_seconds INTEGER,
                reactions_total INTEGER,
                reactions_like INTEGER,
                reactions_readinglist INTEGER,
                reactions_unicorn INTEGER,
                comments_total INTEGER,
                follows_total INTEGER,
                collected_at TIMESTAMP NOT NULL,
                UNIQUE(article_id, date)
            )
        """)
        
        # Table: referrers (from /api/analytics/referrers - UNDOCUMENTED!)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referrers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                domain TEXT,
                count INTEGER NOT NULL,
                collected_at TIMESTAMP NOT NULL,
                UNIQUE(article_id, domain, collected_at)
            )
        """)
        
        # Index pour performances
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_article_metrics_date ON article_metrics(collected_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_article_metrics_article ON article_metrics(article_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_article ON comments(article_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_date ON comments(collected_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_analytics_article ON daily_analytics(article_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_analytics_date ON daily_analytics(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_referrers_article ON referrers(article_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_referrers_domain ON referrers(domain)")
        
        self.conn.commit()
        print("✅ Database initialized")
    
    def collect_snapshot(self):
        """Collect a complete snapshot of all metrics"""
        timestamp = datetime.now(timezone.utc)
        print(f"\n📸 Collecting snapshot at {timestamp.isoformat()}")
        
        # 1. Articles metrics
        articles = self._fetch_articles()
        self._save_article_metrics(articles, timestamp)
        
        # 2. Global snapshot
        self._save_global_snapshot(articles, timestamp)
        
        # 3. Followers
        follower_count = self._fetch_and_save_followers(timestamp)
        
        # 4. Comments (optionnel, peut être long)
        # self._fetch_and_save_comments(articles, timestamp)
        
        # 5. Daily Analytics (optionnel, endpoint non-documenté)
        # Décommentez pour collecter read time, reaction breakdown, etc.
        # self._fetch_and_save_daily_analytics(articles, timestamp)
        
        # 6. Referrers / Traffic Sources (optionnel, endpoint non-documenté!)
        # Décommentez pour collecter les sources de trafic
        # self._fetch_and_save_referrers(articles, timestamp)
        
        self.conn.commit()
        print(f"✅ Snapshot complete: {len(articles)} articles tracked")
    
    def _fetch_articles(self) -> List[Dict]:
        """Fetch all user articles"""
        response = requests.get(
            f"{self.base_url}/articles/me/all",
            headers=self.headers,
            params={"per_page": 1000}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error fetching articles: {response.status_code}")
            return []
    
    def _save_article_metrics(self, articles: List[Dict], timestamp: datetime):
        """Save article metrics to database"""
        cursor = self.conn.cursor()
        
        for article in articles:
            if not article.get('published_at'):
                continue  # Skip drafts
                
            cursor.execute("""
                INSERT OR IGNORE INTO article_metrics 
                (collected_at, article_id, title, slug, published_at, views, 
                 reactions, comments, reading_time_minutes, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp.isoformat(),  # Convert to string
                article['id'],
                article['title'],
                article['slug'],
                article['published_at'],
                article.get('page_views_count', 0),
                article.get('public_reactions_count', 0),
                article.get('comments_count', 0),
                article.get('reading_time_minutes', 0),
                json.dumps(article.get('tag_list', []))
            ))
    
    def _save_global_snapshot(self, articles: List[Dict], timestamp: datetime):
        """Save global snapshot"""
        cursor = self.conn.cursor()
        
        published_articles = [a for a in articles if a.get('published_at')]
        total_views = sum(a.get('page_views_count', 0) for a in published_articles)
        total_reactions = sum(a.get('public_reactions_count', 0) for a in published_articles)
        total_comments = sum(a.get('comments_count', 0) for a in published_articles)
        
        cursor.execute("""
            INSERT OR IGNORE INTO snapshots 
            (collected_at, total_articles, total_views, total_reactions, 
             total_comments, follower_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            timestamp.isoformat(),  # Convert to string
            len(published_articles),
            total_views,
            total_reactions,
            total_comments,
            0  # Will be updated by follower tracking
        ))
    
    def _fetch_and_save_followers(self, timestamp: datetime) -> int:
        """Fetch and save follower information"""
        try:
            # Get total follower count
            response = requests.get(
                f"{self.base_url}/followers/users",
                headers=self.headers,
                params={"per_page": 1}
            )
            
            if response.status_code != 200:
                print(f"⚠️  Could not fetch followers: {response.status_code}")
                return 0
            
            # Fetch all followers with pagination
            all_followers = []
            page = 1
            while True:
                response = requests.get(
                    f"{self.base_url}/followers/users",
                    headers=self.headers,
                    params={"per_page": 80, "page": page}
                )
                
                if response.status_code != 200:
                    break
                    
                followers = response.json()
                if not followers:
                    break
                    
                all_followers.extend(followers)
                page += 1
            
            follower_count = len(all_followers)
            
            # Get previous count to calculate new followers
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT follower_count FROM follower_events 
                ORDER BY collected_at DESC LIMIT 1
            """)
            result = cursor.fetchone()
            previous_count = result[0] if result else 0
            
            new_followers = follower_count - previous_count
            
            # Save event
            cursor.execute("""
                INSERT OR IGNORE INTO follower_events 
                (collected_at, follower_count, new_followers_since_last)
                VALUES (?, ?, ?)
            """, (timestamp.isoformat(), follower_count, new_followers))
            
            # Save individual followers (optional - can be large)
            # for follower in all_followers:
            #     cursor.execute("""
            #         INSERT OR IGNORE INTO followers 
            #         (collected_at, follower_id, username, name, followed_at, profile_image)
            #         VALUES (?, ?, ?, ?, ?, ?)
            #     """, (
            #         timestamp,
            #         follower.get('user_id'),
            #         follower.get('username'),
            #         follower.get('name'),
            #         follower.get('created_at'),
            #         follower.get('profile_image')
            #     ))
            
            # Update snapshot with follower count
            cursor.execute("""
                UPDATE snapshots 
                SET follower_count = ? 
                WHERE collected_at = ?
            """, (follower_count, timestamp.isoformat()))
            
            print(f"👥 Followers: {follower_count} (+{new_followers} since last check)")
            return follower_count
            
        except Exception as e:
            print(f"⚠️  Error tracking followers: {e}")
            return 0
    
    def _fetch_and_save_comments(self, articles: List[Dict], timestamp: datetime):
        """Fetch and save comments for all articles"""
        cursor = self.conn.cursor()
        total_new_comments = 0
        
        for article in articles:
            if not article.get('published_at'):
                continue
                
            try:
                response = requests.get(
                    f"{self.base_url}/comments",
                    params={"a_id": article['id']}
                )
                
                if response.status_code == 200:
                    comments = response.json()
                    
                    for comment in comments:
                        # Save top-level comment
                        saved = self._save_comment(
                            comment, article['id'], article['title'], timestamp, cursor
                        )
                        if saved:
                            total_new_comments += 1
                        
                        # Save nested comments
                        if 'children' in comment:
                            for child in comment['children']:
                                saved = self._save_comment(
                                    child, article['id'], article['title'], timestamp, cursor
                                )
                                if saved:
                                    total_new_comments += 1
            except Exception as e:
                print(f"⚠️  Error fetching comments for article {article['id']}: {e}")
        
        print(f"💬 Comments: {total_new_comments} new comments saved")
    
    def _save_comment(self, comment: Dict, article_id: int, article_title: str, 
                      timestamp: datetime, cursor) -> bool:
        """Sauvegarde un commentaire avec son contenu Markdown (pour spaCy)"""
        comment_id = comment.get('id_code')
        
        # On vérifie si on l'a déjà pour ne pas gaspiller d'appels API
        cursor.execute("SELECT 1 FROM comments WHERE comment_id = ?", (comment_id,))
        if cursor.fetchone():
            return False

        # Appel supplémentaire pour le Markdown
        body_markdown = ""
        try:
            detail_res = requests.get(f"{self.base_url}/comments/{comment_id}")
            if detail_res.status_code == 200:
                body_markdown = detail_res.json().get('body_markdown', '')
        except:
            pass

        cursor.execute("""
            INSERT OR IGNORE INTO comments 
            (collected_at, comment_id, article_id, article_title, created_at,
            author_username, author_name, body_html, body_markdown) -- Nouveau champ
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp.isoformat(),
            comment_id,
            article_id,
            article_title,
            comment.get('created_at'),
            comment.get('user', {}).get('username'),
            comment.get('user', {}).get('name'),
            comment.get('body_html'),
            body_markdown # Le texte propre pour spaCy
        ))
        return True
    
    def _fetch_and_save_daily_analytics(self, articles: List[Dict], timestamp: datetime):
        """Fetch daily analytics from /api/analytics/historical (undocumented endpoint)"""
        from datetime import timedelta
        
        cursor = self.conn.cursor()
        total_new_days = 0
        
        # Calculate start date (90 days ago)
        start_date = (datetime.now(timezone.utc) - timedelta(days=90)).date()
        
        print(f"\n📊 Collecting daily analytics (last 90 days)...")
        
        for article in articles:
            if not article.get('published_at'):
                continue
            
            article_id = article['id']
            
            try:
                # Call undocumented analytics endpoint
                response = requests.get(
                    f"{self.base_url}/analytics/historical",
                    headers=self.headers,
                    params={
                        "start": start_date.isoformat(),
                        "article_id": article_id
                    }
                )
                
                if response.status_code == 200:
                    analytics_data = response.json()
                    
                    for date_str, day_data in analytics_data.items():
                        # Parse date
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                        except:
                            continue
                        
                        # Extract metrics
                        page_views = day_data.get('page_views', {})
                        reactions = day_data.get('reactions', {})
                        comments = day_data.get('comments', {})
                        follows = day_data.get('follows', {})
                        
                        # Save to database (INSERT OR REPLACE to handle updates)
                        cursor.execute("""
                            INSERT OR REPLACE INTO daily_analytics 
                            (article_id, date, page_views, average_read_time_seconds, 
                             total_read_time_seconds, reactions_total, reactions_like, 
                             reactions_readinglist, reactions_unicorn, comments_total,
                             follows_total, collected_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            article_id,
                            date_obj.isoformat(),
                            page_views.get('total', 0),
                            page_views.get('average_read_time_in_seconds', 0),
                            page_views.get('total_read_time_in_seconds', 0),
                            reactions.get('total', 0),
                            reactions.get('like', 0),
                            reactions.get('readinglist', 0),
                            reactions.get('unicorn', 0),
                            comments.get('total', 0),
                            follows.get('total', 0),
                            timestamp.isoformat()
                        ))
                        
                        if cursor.rowcount > 0:
                            total_new_days += 1
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️  Error fetching analytics for article {article_id}: {e}")
        
        print(f"📊 Daily analytics: {total_new_days} day-records updated")
    
    def _fetch_and_save_referrers(self, articles: List[Dict], timestamp: datetime):
        """Fetch referrers from /api/analytics/referrers (undocumented endpoint!)"""
        from datetime import timedelta
        
        cursor = self.conn.cursor()
        total_new_referrers = 0
        
        # Calculate start date (90 days ago)
        start_date = (datetime.now(timezone.utc) - timedelta(days=90)).date()
        
        print(f"\n🌐 Collecting referrers (traffic sources, last 90 days)...")
        
        for article in articles:
            if not article.get('published_at'):
                continue
            
            article_id = article['id']
            
            try:
                # Call undocumented referrers endpoint
                response = requests.get(
                    f"{self.base_url}/analytics/referrers",
                    headers=self.headers,
                    params={
                        "start": start_date.isoformat(),
                        "article_id": article_id
                    }
                )
                
                if response.status_code == 200:
                    referrers_data = response.json()
                    
                    # Extract domains list
                    domains = referrers_data.get('domains', [])
                    
                    for domain_data in domains:
                        domain = domain_data.get('domain')  # Can be None for direct traffic
                        count = domain_data.get('count', 0)
                        
                        # Save to database (INSERT OR REPLACE to handle updates)
                        cursor.execute("""
                            INSERT OR REPLACE INTO referrers 
                            (article_id, domain, count, collected_at)
                            VALUES (?, ?, ?, ?)
                        """, (
                            article_id,
                            domain,
                            count,
                            timestamp.isoformat()
                        ))
                        
                        if cursor.rowcount > 0:
                            total_new_referrers += 1
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️  Error fetching referrers for article {article_id}: {e}")
        
        print(f"🌐 Referrers: {total_new_referrers} domain records updated")
    
    def analyze_growth(self, days: int = 30):
        """Analyze growth trends over time"""
        self.connect_db()
        cursor = self.conn.cursor()
        
        # Article performance over time
        print(f"\n📈 GROWTH ANALYSIS (Last {days} days)")
        print("=" * 80)
        
        cursor.execute("""
            SELECT 
                DATE(collected_at) as date,
                SUM(views) as total_views,
                SUM(reactions) as total_reactions,
                SUM(comments) as total_comments
            FROM article_metrics
            WHERE collected_at >= datetime('now', '-{} days')
            GROUP BY DATE(collected_at)
            ORDER BY date DESC
        """.format(days))
        
        print(f"\n{'Date':<12} {'Views':<10} {'Reactions':<12} {'Comments'}")
        print("-" * 80)
        for row in cursor.fetchall():
            print(f"{row[0]:<12} {row[1]:<10} {row[2]:<12} {row[3]}")
    
    def analyze_article_velocity(self, article_id: int):
        """Analyze a specific article's growth velocity"""
        self.connect_db()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT collected_at, views, reactions, comments
            FROM article_metrics
            WHERE article_id = ?
            ORDER BY collected_at
        """, (article_id,))
        
        rows = cursor.fetchall()
        
        if not rows:
            print(f"❌ No data found for article {article_id}")
            return
        
        print(f"\n🚀 ARTICLE VELOCITY ANALYSIS (Article #{article_id})")
        print("=" * 80)
        print(f"\n{'Timestamp':<20} {'Views':<10} {'Δ Views':<10} {'Reactions':<12} {'Comments'}")
        print("-" * 80)
        
        prev_views = 0
        for row in rows:
            timestamp, views, reactions, comments = row
            delta_views = views - prev_views
            print(f"{timestamp:<20} {views:<10} {delta_views:+<10} {reactions:<12} {comments}")
            prev_views = views
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='DEV.to Metrics Tracker - Historical data collection'
    )
    
    parser.add_argument('--api-key', required=True, help='Your Dev.to API key')
    parser.add_argument('--db', default='devto_metrics.db', help='Database file path')
    parser.add_argument('--init', action='store_true', help='Initialize database')
    parser.add_argument('--collect', action='store_true', help='Collect snapshot')
    parser.add_argument('--collect-daily', action='store_true', 
                       help='Collect daily analytics (read time, reaction breakdown)')
    parser.add_argument('--collect-referrers', action='store_true',
                       help='Collect referrers/traffic sources (NEWLY DISCOVERED!)')
    parser.add_argument('--analyze-growth', type=int, metavar='DAYS', 
                       help='Analyze growth trends')
    parser.add_argument('--analyze-article', type=int, metavar='ARTICLE_ID',
                       help='Analyze specific article velocity')
    
    args = parser.parse_args()
    
    tracker = DevToTracker(args.api_key, args.db)
    
    if args.init:
        tracker.init_db()
    
    if args.collect:
        tracker.init_db()  # Ensure DB exists
        tracker.collect_snapshot()
    
    if args.collect_daily:
        tracker.init_db()  # Ensure DB exists
        tracker.conn = sqlite3.connect(tracker.db_path)
        articles = tracker._fetch_articles()
        timestamp = datetime.now(timezone.utc)
        tracker._fetch_and_save_daily_analytics(articles, timestamp)
        tracker.conn.commit()
        tracker.close()
    
    if args.collect_referrers:
        tracker.init_db()  # Ensure DB exists
        tracker.conn = sqlite3.connect(tracker.db_path)
        articles = tracker._fetch_articles()
        timestamp = datetime.now(timezone.utc)
        tracker._fetch_and_save_referrers(articles, timestamp)
        tracker.conn.commit()
        tracker.close()
    
    if args.analyze_growth:
        tracker.analyze_growth(args.analyze_growth)
    
    if args.analyze_article:
        tracker.analyze_article_velocity(args.analyze_article)
    
    tracker.close()


if __name__ == "__main__":
    main()