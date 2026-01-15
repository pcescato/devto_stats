#!/usr/bin/env python3
"""
Traffic Analytics - Analyze referrers and traffic sources
Based on data from /api/analytics/referrers endpoint (UNDOCUMENTED!)

⚠️ IMPORTANT DATA PERIOD NOTES:
- Referrer data covers last 90 days only
- For articles older than 90 days, traffic metrics are incomplete
- Views/week calculations adjusted to use actual data period (not article age)
"""

import sqlite3
import argparse
from datetime import datetime

class TrafficAnalytics:
    def __init__(self, db_path: str = "devto_metrics.db"):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to database"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
    
    def show_traffic_dashboard(self):
        """Show complete traffic sources dashboard"""
        self.connect()
        
        print("\n" + "="*100)
        print("🌐 TRAFFIC SOURCES DASHBOARD")
        print("="*100)
        
        self.show_top_referrers()
        self.show_article_traffic_breakdown()
        self.show_seo_performance()
        self.show_social_performance()
        
        print("\n" + "="*100)
    
    def show_top_referrers(self):
        """Show top traffic sources across all articles"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT MAX(collected_at) as latest_collection FROM referrers")
        latest = cursor.fetchone()['latest_collection']
        
        if not latest:
            print("\n❌ No referrer data found.")
            return
        
        cursor.execute("""
            SELECT 
                COALESCE(domain, 'Direct / Bookmarks') as source,
                SUM(count) as total_views,
                COUNT(DISTINCT article_id) as articles_count
            FROM referrers
            WHERE collected_at = ?
            GROUP BY domain
            ORDER BY total_views DESC
        """, (latest,))
        
        referrers = cursor.fetchall()
        total_views = sum(r['total_views'] for r in referrers)
        
        print(f"\n\n🌐 TOP TRAFFIC SOURCES (Latest: {latest[:10]})")
        print("-" * 100)
        print(f"{'Source':<40} {'Views':>12} {'% of Total':>12} {'Articles':>12}")
        print("-" * 100)
        
        for ref in referrers:
            source = (ref['source'][:37] + "...") if len(ref['source']) > 40 else ref['source']
            percentage = (ref['total_views'] / total_views * 100) if total_views > 0 else 0
            print(f"{source:<40} {ref['total_views']:>12} {percentage:>11.1f}% {ref['articles_count']:>12}")

    def show_seo_performance(self):
        """Analyze SEO performance (Google traffic) with fixed velocity calculation"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT MAX(collected_at) as latest_collection FROM referrers")
        latest = cursor.fetchone()['latest_collection']
        
        # Correction : On récupère le nombre de jours réels de données via daily_analytics
        cursor.execute("""
            SELECT 
                r.article_id,
                am.title,
                SUM(r.count) as google_views,
                am.published_at,
                julianday('now') - julianday(am.published_at) as article_age_days,
                (
                    SELECT COUNT(DISTINCT date)
                    FROM daily_analytics da
                    WHERE da.article_id = r.article_id
                ) as actual_days_with_data
            FROM referrers r
            JOIN (
                SELECT DISTINCT article_id, title, published_at
                FROM article_metrics
                WHERE published_at IS NOT NULL
            ) am ON r.article_id = am.article_id
            WHERE r.collected_at = ?
            AND r.domain LIKE '%google%'
            GROUP BY r.article_id
            HAVING google_views > 5
            ORDER BY google_views DESC
            LIMIT 10
        """, (latest,))
        
        articles = cursor.fetchall()
        
        print(f"\n\n🔍 SEO PERFORMANCE (Articles with Google Traffic)")
        print("-" * 120)
        print(f"{'Article':<40} {'Age':>8} {'Data':>6} {'Google':>10} {'Views/Week':>12} {'Note':<15}")
        print("-" * 120)
        
        for article in articles:
            title = (article['title'][:37] + "...") if len(article['title']) > 40 else article['title']
            age = int(article['article_age_days']) if article['article_age_days'] else 0
            
            # Pragmatique : Si l'article a plus de 90 jours, on divise par 90 (la fenêtre de l'API)
            # Sinon on divise par le nombre de jours réels où on a de la donnée
            data_days = article['actual_days_with_data'] or 1
            data_period_days = min(90, data_days)
            views_per_week = (article['google_views'] / data_period_days) * 7
            
            note = "⚠️ >90d (Recent)" if age > 90 else ""
            
            print(f"{title:<40} {age:>7}d {data_days:>5}d {article['google_views']:>10} "
                  f"{views_per_week:>11.1f} {note:<15}")

    # ... (les autres méthodes comme show_social_performance restent identiques)

def main():
    parser = argparse.ArgumentParser(description="Traffic Sources Analytics Dashboard")
    parser.add_argument('--db', default='devto_metrics.db', help='Database path')
    parser.add_argument('--full', action='store_true', help='Show full dashboard')
    parser.add_argument('--seo', action='store_true', help='SEO performance')
    
    args = parser.parse_args()
    analytics = TrafficAnalytics(args.db)
    
    if args.seo or args.full:
        analytics.connect()
        analytics.show_seo_performance()

if __name__ == "__main__":
    main()