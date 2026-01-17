#!/usr/bin/env python3
"""
List Articles - Simple utility to list all your articles with IDs
Usage: python3 list_articles.py [options]
"""

import sqlite3
import argparse
from datetime import datetime

class ArticleLister:
    def __init__(self, db_path: str = "devto_metrics.db"):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to database"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
    
    def list_all_articles(self, sort_by: str = "published", limit: int = None, include_deleted: bool = False):
        """List all articles with IDs"""
        self.connect()
        cursor = self.conn.cursor()
        
        # Build order by clause
        order_by = {
            "published": "published_at DESC",
            "views": "views DESC",
            "reactions": "reactions DESC",
            "comments": "comments DESC",
            "title": "title ASC",
            "id": "article_id ASC"
        }.get(sort_by, "published_at DESC")
        
        # Filter deleted articles unless explicitly requested
        deleted_filter = "" if include_deleted else "AND (is_deleted IS NULL OR is_deleted = 0)"
        
        query = f"""
            SELECT 
                article_id,
                title,
                published_at,
                MAX(views) as views,
                MAX(reactions) as reactions,
                MAX(comments) as comments,
                MAX(is_deleted) as is_deleted
            FROM article_metrics
            WHERE published_at IS NOT NULL
            {deleted_filter}
            GROUP BY article_id
            ORDER BY {order_by}
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        articles = cursor.fetchall()
        
        if not articles:
            print("\n❌ No articles found in database")
            print("Run: python3 devto_tracker.py --api-key YOUR_KEY --collect")
            return
        
        status_msg = "including deleted" if include_deleted else "active only"
        
        print("\n" + "="*100)
        print(f"📚 YOUR ARTICLES (Total: {len(articles)}, {status_msg})")
        print("="*100)
        print(f"\n{'ID':<10} {'Title':<50} {'Published':<12} {'Views':>8} {'👍':>6} {'💬':>6}")
        print("-"*100)
        
        for article in articles:
            title = article['title'][:47] + "..." if len(article['title']) > 50 else article['title']
            pub_date = article['published_at'][:10] if article['published_at'] else 'N/A'
            
            # Mark deleted articles
            deleted_marker = " 🗑️" if article['is_deleted'] else ""
            title = title + deleted_marker
            
            print(f"{article['article_id']:<10} {title:<50} {pub_date:<12} "
                  f"{article['views']:>8} {article['reactions']:>6} {article['comments']:>6}")
        
        if not include_deleted:
            print("\n💡 To see deleted articles: python3 list_articles.py --include-deleted")
        
        print("\n💡 Use article ID with other commands:")
        print("   python3 quality_analytics.py --article <ID>")
        print("   python3 traffic_analytics.py --article <ID>")
        print("   python3 comment_analyzer.py --article <ID>")
        print("   python3 advanced_analytics.py --evolution <ID>")
    
    def search_articles(self, search_term: str):
        """Search articles by title"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                article_id,
                title,
                published_at,
                MAX(views) as views,
                MAX(reactions) as reactions,
                MAX(comments) as comments
            FROM article_metrics
            WHERE title LIKE ?
            GROUP BY article_id
            ORDER BY published_at DESC
        """, (f"%{search_term}%",))
        
        articles = cursor.fetchall()
        
        if not articles:
            print(f"\n❌ No articles found matching '{search_term}'")
            return
        
        print("\n" + "="*100)
        print(f"🔍 SEARCH RESULTS for '{search_term}' ({len(articles)} found)")
        print("="*100)
        print(f"\n{'ID':<10} {'Title':<50} {'Published':<12} {'Views':>8} {'👍':>6} {'💬':>6}")
        print("-"*100)
        
        for article in articles:
            title = article['title'][:47] + "..." if len(article['title']) > 50 else article['title']
            pub_date = article['published_at'][:10] if article['published_at'] else 'N/A'
            
            print(f"{article['article_id']:<10} {title:<50} {pub_date:<12} "
                  f"{article['views']:>8} {article['reactions']:>6} {article['comments']:>6}")
    
    def show_article_details(self, article_id: int):
        """Show detailed info for specific article"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                article_id,
                title,
                slug,
                published_at,
                MAX(views) as views,
                MAX(reactions) as reactions,
                MAX(comments) as comments,
                reading_time_minutes,
                tags
            FROM article_metrics
            WHERE article_id = ?
            GROUP BY article_id
        """, (article_id,))
        
        article = cursor.fetchone()
        
        if not article:
            print(f"\n❌ Article {article_id} not found")
            return
        
        print("\n" + "="*100)
        print(f"📄 ARTICLE DETAILS")
        print("="*100)
        print(f"\nID:           {article['article_id']}")
        print(f"Title:        {article['title']}")
        print(f"Slug:         {article['slug']}")
        print(f"Published:    {article['published_at'][:19] if article['published_at'] else 'N/A'}")
        print(f"Reading time: {article['reading_time_minutes']} minutes")
        
        if article['tags']:
            import json
            try:
                tags = json.loads(article['tags'])
                print(f"Tags:         {', '.join(tags)}")
            except:
                print(f"Tags:         {article['tags']}")
        
        print(f"\n📊 METRICS:")
        print(f"Views:        {article['views']:,}")
        print(f"Reactions:    {article['reactions']:,}")
        print(f"Comments:     {article['comments']:,}")
        
        if article['views'] > 0:
            engagement = ((article['reactions'] + article['comments']) / article['views']) * 100
            print(f"Engagement:   {engagement:.2f}%")
        
        # Check for additional data
        cursor.execute("""
            SELECT COUNT(*) as days
            FROM daily_analytics
            WHERE article_id = ?
        """, (article_id,))
        
        daily_count = cursor.fetchone()['days']
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM comments
            WHERE article_id = ?
        """, (article_id,))
        
        comment_count = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(DISTINCT domain) as sources
            FROM referrers
            WHERE article_id = ?
        """, (article_id,))
        
        referrer_count = cursor.fetchone()['sources']
        
        print(f"\n📈 AVAILABLE ANALYTICS:")
        print(f"Daily analytics:   {daily_count} days of data")
        print(f"Comments tracked:  {comment_count} comments")
        print(f"Traffic sources:   {referrer_count} sources")
        
        print(f"\n💡 ANALYZE THIS ARTICLE:")
        print(f"   python3 quality_analytics.py --article {article_id}")
        print(f"   python3 traffic_analytics.py --article {article_id}")
        print(f"   python3 comment_analyzer.py --article {article_id}")
        print(f"   python3 advanced_analytics.py --evolution {article_id}")
        
        print(f"\n🔗 DEV.TO URL:")
        print(f"   https://dev.to/{article['slug']}")
    
    def list_top_performers(self):
        """Show top performing articles across different metrics"""
        self.connect()
        cursor = self.conn.cursor()
        
        print("\n" + "="*100)
        print("🏆 TOP PERFORMERS")
        print("="*100)
        
        # Top by views
        print("\n📈 TOP 5 BY VIEWS:")
        cursor.execute("""
            SELECT 
                article_id,
                title,
                MAX(views) as views
            FROM article_metrics
            WHERE published_at IS NOT NULL
            GROUP BY article_id
            ORDER BY views DESC
            LIMIT 5
        """)
        
        for i, article in enumerate(cursor.fetchall(), 1):
            title = article['title'][:60] + "..." if len(article['title']) > 60 else article['title']
            print(f"   {i}. [{article['article_id']}] {title}")
            print(f"      {article['views']:,} views")
        
        # Top by reactions
        print("\n💙 TOP 5 BY REACTIONS:")
        cursor.execute("""
            SELECT 
                article_id,
                title,
                MAX(reactions) as reactions
            FROM article_metrics
            WHERE published_at IS NOT NULL
            GROUP BY article_id
            ORDER BY reactions DESC
            LIMIT 5
        """)
        
        for i, article in enumerate(cursor.fetchall(), 1):
            title = article['title'][:60] + "..." if len(article['title']) > 60 else article['title']
            print(f"   {i}. [{article['article_id']}] {title}")
            print(f"      {article['reactions']:,} reactions")
        
        # Top by comments
        print("\n💬 TOP 5 BY COMMENTS:")
        cursor.execute("""
            SELECT 
                article_id,
                title,
                MAX(comments) as comments
            FROM article_metrics
            WHERE published_at IS NOT NULL
            GROUP BY article_id
            ORDER BY comments DESC
            LIMIT 5
        """)
        
        for i, article in enumerate(cursor.fetchall(), 1):
            title = article['title'][:60] + "..." if len(article['title']) > 60 else article['title']
            print(f"   {i}. [{article['article_id']}] {title}")
            print(f"      {article['comments']:,} comments")
        
        # Top by engagement rate
        print("\n🔥 TOP 5 BY ENGAGEMENT RATE:")
        cursor.execute("""
            SELECT 
                article_id,
                title,
                MAX(views) as views,
                MAX(reactions) as reactions,
                MAX(comments) as comments,
                (CAST(MAX(reactions) + MAX(comments) AS FLOAT) / MAX(views)) * 100 as engagement
            FROM article_metrics
            WHERE published_at IS NOT NULL
            AND views > 50
            GROUP BY article_id
            ORDER BY engagement DESC
            LIMIT 5
        """)
        
        for i, article in enumerate(cursor.fetchall(), 1):
            title = article['title'][:60] + "..." if len(article['title']) > 60 else article['title']
            print(f"   {i}. [{article['article_id']}] {title}")
            print(f"      {article['engagement']:.2f}% engagement ({article['views']} views)")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='List Articles - Find article IDs for analysis'
    )
    
    parser.add_argument('--db', default='devto_metrics.db', help='Database file path')
    parser.add_argument('--all', action='store_true', help='List all articles (default)')
    parser.add_argument('--sort', choices=['published', 'views', 'reactions', 'comments', 'title', 'id'],
                       default='published', help='Sort by (default: published)')
    parser.add_argument('--limit', type=int, metavar='N', help='Limit number of results')
    parser.add_argument('--search', type=str, metavar='TERM', help='Search articles by title')
    parser.add_argument('--id', type=int, metavar='ID', help='Show details for specific article')
    parser.add_argument('--top', action='store_true', help='Show top performers')
    parser.add_argument('--include-deleted', action='store_true', help='Include deleted articles in results')
    
    args = parser.parse_args()
    
    lister = ArticleLister(args.db)
    
    if args.id:
        lister.show_article_details(args.id)
    elif args.search:
        lister.search_articles(args.search)
    elif args.top:
        lister.list_top_performers()
    else:
        # Default: list all articles
        lister.list_all_articles(sort_by=args.sort, limit=args.limit, include_deleted=args.include_deleted)
    
    lister.close()


if __name__ == "__main__":
    main()