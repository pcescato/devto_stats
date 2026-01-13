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
        
        # Get most recent collection
        cursor.execute("""
            SELECT MAX(collected_at) as latest_collection
            FROM referrers
        """)
        
        latest = cursor.fetchone()['latest_collection']
        
        if not latest:
            print("\n❌ No referrer data found. Run: python3 devto_tracker.py --api-key YOUR_KEY --collect-referrers")
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
        
        if not referrers:
            print("\n❌ No referrer data available")
            return
        
        total_views = sum(r['total_views'] for r in referrers)
        
        print(f"\n\n🌐 TOP TRAFFIC SOURCES (Latest: {latest[:10]})")
        print("-" * 100)
        print(f"{'Source':<40} {'Views':>12} {'% of Total':>12} {'Articles':>12}")
        print("-" * 100)
        
        for ref in referrers:
            source = ref['source'][:37] + "..." if len(ref['source']) > 40 else ref['source']
            views = ref['total_views']
            percentage = (views / total_views * 100) if total_views > 0 else 0
            articles = ref['articles_count']
            
            print(f"{source:<40} {views:>12} {percentage:>11.1f}% {articles:>12}")
        
        print("-" * 100)
        print(f"{'TOTAL':<40} {total_views:>12} {'100.0%':>12}")
    
    def show_article_traffic_breakdown(self):
        """Show traffic breakdown per article"""
        cursor = self.conn.cursor()
        
        # Get most recent collection
        cursor.execute("""
            SELECT MAX(collected_at) as latest_collection
            FROM referrers
        """)
        
        latest = cursor.fetchone()['latest_collection']
        
        cursor.execute("""
            SELECT 
                r.article_id,
                am.title,
                SUM(CASE WHEN r.domain IS NULL THEN r.count ELSE 0 END) as direct,
                SUM(CASE WHEN r.domain = 'dev.to' THEN r.count ELSE 0 END) as devto_internal,
                SUM(CASE WHEN r.domain LIKE '%google%' THEN r.count ELSE 0 END) as google,
                SUM(CASE WHEN r.domain IN ('t.co', 'x.com', 'twitter.com') THEN r.count ELSE 0 END) as twitter,
                SUM(CASE WHEN r.domain = 'linkedin.com' THEN r.count ELSE 0 END) as linkedin,
                SUM(CASE WHEN r.domain NOT IN ('dev.to') 
                    AND r.domain NOT LIKE '%google%' 
                    AND r.domain NOT IN ('t.co', 'x.com', 'twitter.com', 'linkedin.com')
                    AND r.domain IS NOT NULL THEN r.count ELSE 0 END) as other,
                SUM(r.count) as total
            FROM referrers r
            JOIN (
                SELECT DISTINCT article_id, title
                FROM article_metrics
            ) am ON r.article_id = am.article_id
            WHERE r.collected_at = ?
            GROUP BY r.article_id
            ORDER BY total DESC
            LIMIT 10
        """, (latest,))
        
        articles = cursor.fetchall()
        
        print(f"\n\n📊 TRAFFIC BREAKDOWN BY ARTICLE (Top 10)")
        print("-" * 100)
        print(f"{'Article':<40} {'Direct':>8} {'DEV.to':>8} {'Google':>8} {'Twitter':>8} {'Other':>8} {'Total':>8}")
        print("-" * 100)
        
        for article in articles:
            title = article['title'][:37] + "..." if len(article['title']) > 40 else article['title']
            
            print(f"{title:<40} "
                  f"{article['direct']:>8} "
                  f"{article['devto_internal']:>8} "
                  f"{article['google']:>8} "
                  f"{article['twitter']:>8} "
                  f"{article['other']:>8} "
                  f"{article['total']:>8}")
    
    def show_seo_performance(self):
        """Analyze SEO performance (Google traffic)"""
        cursor = self.conn.cursor()
        
        # Get most recent collection
        cursor.execute("""
            SELECT MAX(collected_at) as latest_collection
            FROM referrers
        """)
        
        latest = cursor.fetchone()['latest_collection']
        
        # FIXED: Calculate views/week using actual data period
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
        
        if not articles:
            print(f"\n\n🔍 SEO PERFORMANCE")
            print("-" * 100)
            print("No significant Google traffic found (minimum 5 views)")
            return
        
        print(f"\n\n🔍 SEO PERFORMANCE (Articles with Google Traffic)")
        print("-" * 120)
        print(f"{'Article':<40} {'Age':>8} {'Data':>6} {'Google':>10} {'Views/Week':>12} {'Note':<15}")
        print("-" * 120)
        
        for article in articles:
            title = article['title'][:37] + "..." if len(article['title']) > 40 else article['title']
            article_age_days = int(article['article_age_days']) if article['article_age_days'] else 0
            data_days = article['actual_days_with_data'] or 90  # Default to 90 if no daily_analytics
            google_views = article['google_views']
            
            # FIXED: Use actual data period for calculation (max 90 days)
            # This prevents under-estimation for old articles
            data_period_days = min(90, max(data_days, 1))
            views_per_week = (google_views / data_period_days) * 7
            
            # Note if data might be incomplete
            note = ""
            if article_age_days > 90:
                note = "⚠️ Incomplete"
            
            print(f"{title:<40} {article_age_days:>7}d {data_days:>5}d {google_views:>10} "
                  f"{views_per_week:>11.1f} {note:<15}")
        
        # Calculate total SEO power
        cursor.execute("""
            SELECT 
                SUM(r.count) as total_google_views,
                COUNT(DISTINCT r.article_id) as articles_with_google
            FROM referrers r
            WHERE r.collected_at = ?
            AND r.domain LIKE '%google%'
        """, (latest,))
        
        totals = cursor.fetchone()
        
        print("-" * 120)
        print("\n💡 SEO Summary:")
        print(f"  • Total Google views: {totals['total_google_views']}")
        print(f"  • Articles with Google traffic: {totals['articles_with_google']}")
        print(f"  ⚠️ Views/week calculated on actual data period (max 90 days)")
        print(f"     For articles >90 days old, this reflects recent performance only")
    
    def show_social_performance(self):
        """Analyze social media performance"""
        cursor = self.conn.cursor()
        
        # Get most recent collection
        cursor.execute("""
            SELECT MAX(collected_at) as latest_collection
            FROM referrers
        """)
        
        latest = cursor.fetchone()['latest_collection']
        
        # Get social media breakdown
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN domain IN ('t.co', 'x.com', 'twitter.com') THEN 'Twitter/X'
                    WHEN domain = 'linkedin.com' THEN 'LinkedIn'
                    WHEN domain = 'facebook.com' THEN 'Facebook'
                    WHEN domain = 'reddit.com' THEN 'Reddit'
                    WHEN domain = 'news.ycombinator.com' THEN 'Hacker News'
                    ELSE 'Other Social'
                END as platform,
                SUM(count) as total_views,
                COUNT(DISTINCT article_id) as articles_count
            FROM referrers
            WHERE collected_at = ?
            AND domain IN ('t.co', 'x.com', 'twitter.com', 'linkedin.com', 
                          'facebook.com', 'reddit.com', 'news.ycombinator.com')
            GROUP BY platform
            ORDER BY total_views DESC
        """, (latest,))
        
        platforms = cursor.fetchall()
        
        if not platforms:
            print(f"\n\n📱 SOCIAL MEDIA PERFORMANCE")
            print("-" * 100)
            print("No social media traffic found")
            return
        
        print(f"\n\n📱 SOCIAL MEDIA PERFORMANCE")
        print("-" * 100)
        print(f"{'Platform':<20} {'Views':>12} {'Articles':>12} {'Avg per Article':>15}")
        print("-" * 100)
        
        for platform in platforms:
            avg_per_article = platform['total_views'] / platform['articles_count'] if platform['articles_count'] > 0 else 0
            
            print(f"{platform['platform']:<20} "
                  f"{platform['total_views']:>12} "
                  f"{platform['articles_count']:>12} "
                  f"{avg_per_article:>14.1f}")
    
    def analyze_article_sources(self, article_id: int):
        """Show detailed traffic sources for a specific article"""
        cursor = self.conn.cursor()
        
        # Get article info
        cursor.execute("""
            SELECT DISTINCT title, published_at
            FROM article_metrics
            WHERE article_id = ?
        """, (article_id,))
        
        article_info = cursor.fetchone()
        if not article_info:
            print(f"❌ Article {article_id} not found")
            return
        
        print(f"\n🌐 TRAFFIC SOURCES: {article_info['title']}")
        print("-" * 100)
        print(f"Published: {article_info['published_at'][:10] if article_info['published_at'] else 'N/A'}")
        print()
        
        # Get most recent referrers
        cursor.execute("""
            SELECT MAX(collected_at) as latest_collection
            FROM referrers
            WHERE article_id = ?
        """, (article_id,))
        
        latest = cursor.fetchone()['latest_collection']
        
        if not latest:
            print(f"❌ No referrer data for this article")
            return
        
        cursor.execute("""
            SELECT 
                COALESCE(domain, 'Direct / Bookmarks') as source,
                count as views
            FROM referrers
            WHERE article_id = ?
            AND collected_at = ?
            ORDER BY count DESC
        """, (article_id, latest))
        
        sources = cursor.fetchall()
        
        total_views = sum(s['views'] for s in sources)
        
        print(f"{'Source':<50} {'Views':>10} {'%':>8}")
        print("-" * 100)
        
        for source in sources:
            percentage = (source['views'] / total_views * 100) if total_views > 0 else 0
            print(f"{source['source']:<50} {source['views']:>10} {percentage:>7.1f}%")
        
        print("-" * 100)
        print(f"{'TOTAL':<50} {total_views:>10} {'100.0%':>8}")
        print("\n💡 Data reflects last 90 days of traffic")

def main():
    parser = argparse.ArgumentParser(description="Traffic Sources Analytics Dashboard")
    parser.add_argument('--db', default='devto_metrics.db', help='Database path')
    parser.add_argument('--full', action='store_true', help='Show full dashboard')
    parser.add_argument('--referrers', action='store_true', help='Show top referrers')
    parser.add_argument('--by-article', action='store_true', help='Traffic breakdown by article')
    parser.add_argument('--seo', action='store_true', help='SEO performance')
    parser.add_argument('--social', action='store_true', help='Social media performance')
    parser.add_argument('--article', type=int, metavar='ID', help='Detailed sources for article')
    
    args = parser.parse_args()
    
    analytics = TrafficAnalytics(args.db)
    
    # If no specific analysis requested, show full dashboard
    if not any([args.referrers, args.by_article, args.seo, args.social, args.article]):
        args.full = True
    
    if args.full:
        analytics.show_traffic_dashboard()
    else:
        analytics.connect()
        if args.referrers:
            analytics.show_top_referrers()
        if args.by_article:
            analytics.show_article_traffic_breakdown()
        if args.seo:
            analytics.show_seo_performance()
        if args.social:
            analytics.show_social_performance()
    
    if args.article:
        analytics.analyze_article_sources(args.article)

if __name__ == "__main__":
    main()