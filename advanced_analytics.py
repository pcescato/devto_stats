#!/usr/bin/env python3
"""
Advanced Analytics (Version Finalisée) - Pascal Cescato Edition
- Attribution robuste des followers par calcul de delta temporel.
- Auto-détection de l'identifiant auteur pour isoler les réponses (Reply Rate).
- Analyse de l'engagement net des lecteurs.
"""

import sqlite3
import argparse
from datetime import datetime, timedelta
import statistics

class AdvancedAnalytics:
    def __init__(self, db_path: str, author_username: str = "pascal_cescato_692b7a8a20"):
        self.db_path = db_path
        self.author_username = author_username
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def article_follower_correlation(self):
        """
        Calcule le gain de followers réel en comparant les compteurs 
        au plus proche de la date de publication et 7 jours après.
        """
        cursor = self.conn.cursor()
        print("\n📊 ARTICLE → FOLLOWER CORRELATION (ROBUST DELTA)")
        print("=" * 110)
        
        cursor.execute("""
            SELECT article_id, title, published_at, 
                   MAX(views) as total_views
            FROM article_metrics 
            WHERE published_at IS NOT NULL 
            GROUP BY article_id ORDER BY published_at DESC
        """)
        articles = cursor.fetchall()

        print(f"{'Article':<45} {'Date':<12} {'Gain':>8} {'Start':>8} {'End':>8} {'Views':>8}")
        print("-" * 110)

        for art in articles:
            pub_date = art['published_at']
            
            # Point de données le plus proche de la publication
            cursor.execute("""
                SELECT follower_count FROM follower_events 
                ORDER BY ABS(julianday(collected_at) - julianday(?)) ASC LIMIT 1
            """, (pub_date,))
            start = cursor.fetchone()
            
            # Point de données le plus proche de J+7
            target_end = (datetime.fromisoformat(pub_date.replace('Z', '+00:00')) + timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT follower_count FROM follower_events 
                ORDER BY ABS(julianday(collected_at) - julianday(?)) ASC LIMIT 1
            """, (target_end,))
            end = cursor.fetchone()

            if start and end:
                gain = end['follower_count'] - start['follower_count']
                # On n'affiche que les articles ayant un historique de followers cohérent
                if start['follower_count'] != end['follower_count'] or gain != 0:
                    title = (art['title'][:42] + "...") if len(art['title']) > 45 else art['title']
                    print(f"{title:<45} {pub_date[:10]:<12} {gain:>8} {start['follower_count']:>8} {end['follower_count']:>8} {art['total_views']:>8}")

    def comment_engagement_correlation(self):
        """
        Analyse l'impact de tes interactions sur l'engagement global.
        Isole tes réponses du volume total de commentaires des lecteurs.
        """
        cursor = self.conn.cursor()
        
        # Auto-détection de l'auteur par volume de commentaires (sécurité)
        cursor.execute("""
            SELECT author_username FROM comments 
            GROUP BY author_username ORDER BY COUNT(*) DESC LIMIT 1
        """)
        top_user = cursor.fetchone()
        detected_author = top_user['author_username'] if top_user else self.author_username

        print(f"\n💬 AUTHOR INTERACTION ↔ ENGAGEMENT (Detected: @{detected_author})")
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
        """, (detected_author, detected_author))
        
        articles = cursor.fetchall()
        
        print(f"{'Article':<45} {'Readers':>10} {'Author':>10} {'Reply %':>10} {'Engage %':>10}")
        print("-" * 110)
        
        for art in articles:
            reply_rate = (art['author_replies'] / art['reader_comments'] * 100) if art['reader_comments'] > 0 else 0
            # Engagement net : Reactions + Commentaires lecteurs / Vues
            engage_rate = ((art['reactions'] + art['reader_comments']) / art['views'] * 100) if art['views'] > 0 else 0
            
            title = (art['title'][:42] + "...") if len(art['title']) > 45 else art['title']
            print(f"{title:<45} {art['reader_comments']:>10} {art['author_replies']:>10} {reply_rate:>9.1f}% {engage_rate:>9.2f}%")

    def full_report(self):
        """Génère le rapport complet d'analyses avancées."""
        print("\n" + "=" * 110)
        print(" " * 38 + "📊 ADVANCED ANALYTICS REPORT")
        print("=" * 110)
        self.article_follower_correlation()
        self.comment_engagement_correlation()

    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='Advanced Analytics - Pascal Edition')
    parser.add_argument('--db', default='devto_metrics.db', help='Chemin vers la base SQLite')
    # Utilisation de ton ID technique identifié : pascal_cescato_692b7a8a20
    parser.add_argument('--author', default='pascal_cescato_692b7a8a20', help='Ton username DEV.to')
    
    args = parser.parse_args()
    
    analytics = AdvancedAnalytics(args.db, args.author)
    analytics.full_report()
    analytics.close()

if __name__ == "__main__":
    main()