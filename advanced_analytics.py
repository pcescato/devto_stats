#!/usr/bin/env python3
"""
Advanced Analytics (Version Corrigée) - Pascal Cescato Edition
- Fix: Attribution de followers par delta (évite le double comptage)
- New: Isolation de l'engagement auteur (Replies)
"""

import sqlite3
import argparse
from datetime import datetime, timedelta
import statistics

class AdvancedAnalytics:
    def __init__(self, db_path: str, author_username: str = "pascal_cescato"):
        self.db_path = db_path
        self.author_username = author_username
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def article_follower_correlation(self):
        """Corrélation corrigée : Calcule le delta réel de followers autour de la sortie"""
        cursor = self.conn.cursor()
        
        print("\n📊 ARTICLE → FOLLOWER CORRELATION (FIXED DELTA)")
        print("=" * 110)
        
        cursor.execute("""
            SELECT article_id, title, published_at, 
                   MAX(views) as total_views, MAX(reactions) as total_reactions
            FROM article_metrics 
            WHERE published_at IS NOT NULL 
            GROUP BY article_id ORDER BY published_at DESC
        """)
        articles = cursor.fetchall()

        print(f"{'Article':<45} {'Date':<12} {'Gain':>8} {'Start':>8} {'End':>8} {'Views':>8}")
        print("-" * 110)

        for art in articles:
            pub_date = art['published_at']
            # On cherche le nombre de followers juste AVANT la publication
            cursor.execute("""
                SELECT follower_count FROM follower_events 
                WHERE collected_at <= ? ORDER BY collected_at DESC LIMIT 1
            """, (pub_date,))
            start = cursor.fetchone()
            
            # On cherche le nombre de followers 7 jours APRÈS
            end_window = (datetime.fromisoformat(pub_date.replace('Z', '+00:00')) + timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT follower_count FROM follower_events 
                WHERE collected_at >= ? ORDER BY collected_at ASC LIMIT 1
            """, (end_window,))
            end = cursor.fetchone()

            if start and end:
                gain = end['follower_count'] - start['follower_count']
                title = (art['title'][:42] + "...") if len(art['title']) > 45 else art['title']
                print(f"{title:<45} {pub_date[:10]:<12} {gain:>8} {start['follower_count']:>8} {end['follower_count']:>8} {art['total_views']:>8}")

    def comment_engagement_correlation(self):
        """Corrélation: Impact des réponses de l'auteur sur l'engagement"""
        cursor = self.conn.cursor()
        
        print(f"\n💬 AUTHOR INTERACTION ↔ ENGAGEMENT (Author: @{self.author_username})")
        print("=" * 110)
        
        cursor.execute("""
            SELECT 
                am.article_id, am.title,
                MAX(am.views) as views,
                MAX(am.reactions) as reactions,
                (SELECT COUNT(*) FROM comments WHERE article_id = am.article_id AND author_username != ?) as reader_comments,
                (SELECT COUNT(*) FROM comments WHERE article_id = am.article_id AND author_username = ?) as author_replies
            FROM article_metrics am
            WHERE am.published_at IS NOT NULL
            GROUP BY am.article_id
            ORDER BY reader_comments DESC
        """, (self.author_username, self.author_username))
        
        articles = cursor.fetchall()
        
        print(f"{'Article':<45} {'Readers':>10} {'Author':>10} {'Reply %':>10} {'Engage %':>10}")
        print("-" * 110)
        
        for art in articles:
            total_comm = art['reader_comments'] + art['author_replies']
            reply_rate = (art['author_replies'] / art['reader_comments'] * 100) if art['reader_comments'] > 0 else 0
            # Engagement basé uniquement sur les actions des lecteurs (reactions + leurs commentaires)
            engage_rate = ((art['reactions'] + art['reader_comments']) / art['views'] * 100) if art['views'] > 0 else 0
            
            title = (art['title'][:42] + "...") if len(art['title']) > 45 else art['title']
            print(f"{title:<45} {art['reader_comments']:>10} {art['author_replies']:>10} {reply_rate:>9.1f}% {engage_rate:>9.2f}%")

    def full_report(self):
        self.article_follower_correlation()
        self.comment_engagement_correlation()

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='devto_metrics.db')
    parser.add_argument('--author', default='pascal_cescato')
    args = parser.parse_args()
    
    analytics = AdvancedAnalytics(args.db, args.author)
    analytics.full_report()
    analytics.close()