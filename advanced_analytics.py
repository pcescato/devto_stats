#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from datetime import datetime, timedelta
import statistics
import json
from core.database import DatabaseManager

class AdvancedAnalytics:
    def __init__(self, db_path: str, author_username: str = "pascal_cescato_692b7a8a20"):
        self.db = DatabaseManager(db_path)
        self.author_username = author_username

    def article_follower_correlation(self):
        """Calcule le gain de followers réel (Fenêtre +/- 6h)."""
        conn = self.db.get_connection()
        print("\n📊 ARTICLE → FOLLOWER CORRELATION (ROBUST DELTA)")
        print("=" * 110)
        
        articles = conn.execute("""
            SELECT article_id, title, published_at, MAX(views) as total_views
            FROM article_metrics WHERE published_at IS NOT NULL 
            GROUP BY article_id ORDER BY published_at DESC
        """).fetchall()

        print(f"{'Article':<45} {'Date':<12} {'Gain':>8} {'Start':>8} {'End':>8} {'Views':>8}")
        print("-" * 110)

        for art in articles:
            pub_date = art['published_at']
            # Start: J+0
            start = conn.execute("""
                SELECT follower_count FROM follower_events 
                WHERE julianday(collected_at) BETWEEN julianday(?) - 0.25 AND julianday(?) + 0.25
                ORDER BY ABS(julianday(collected_at) - julianday(?)) ASC LIMIT 1
            """, (pub_date, pub_date, pub_date)).fetchone()
            
            # End: J+7
            target_end = (datetime.fromisoformat(pub_date.replace('Z', '+00:00')) + timedelta(days=7)).isoformat()
            end = conn.execute("""
                SELECT follower_count FROM follower_events 
                WHERE julianday(collected_at) BETWEEN julianday(?) - 0.25 AND julianday(?) + 0.25
                ORDER BY ABS(julianday(collected_at) - julianday(?)) ASC LIMIT 1
            """, (target_end, target_end, target_end)).fetchone()

            if start and end:
                gain = end['follower_count'] - start['follower_count']
                if gain != 0 or start['follower_count'] > 0:
                    title = (art['title'][:42] + "...") if len(art['title']) > 45 else art['title']
                    print(f"{title:<45} {pub_date[:10]:<12} {gain:>8} {start['follower_count']:>8} {end['follower_count']:>8} {art['total_views']:>8}")

    def comment_engagement_correlation(self):
        """Analyse l'impact de tes interactions sur l'engagement."""
        conn = self.db.get_connection()
        # Détection auto de l'auteur
        top_user = conn.execute("SELECT author_username FROM comments GROUP BY author_username ORDER BY COUNT(*) DESC LIMIT 1").fetchone()
        detected_author = top_user['author_username'] if top_user else self.author_username

        print(f"\n💬 AUTHOR INTERACTION ↔ ENGAGEMENT (Detected: @{detected_author})")
        print("=" * 110)
        
        articles = conn.execute("""
            SELECT am.article_id, am.title, MAX(am.views) as views, MAX(am.reactions) as reactions,
                (SELECT COUNT(*) FROM comments WHERE article_id = am.article_id AND author_username != ?) as reader_comments,
                (SELECT COUNT(*) FROM comments WHERE article_id = am.article_id AND author_username = ?) as author_replies
            FROM article_metrics am GROUP BY am.article_id ORDER BY reader_comments DESC
        """, (detected_author, detected_author)).fetchall()
        
        print(f"{'Article':<45} {'Readers':>10} {'Author':>10} {'Reply %':>10} {'Engage %':>10}")
        print("-" * 110)
        
        for art in articles:
            reply_rate = (art['author_replies'] / art['reader_comments'] * 100) if art['reader_comments'] > 0 else 0
            engage_rate = ((art['reactions'] + art['reader_comments']) / art['views'] * 100) if art['views'] > 0 else 0
            title = (art['title'][:42] + "...") if len(art['title']) > 45 else art['title']
            print(f"{title:<45} {art['reader_comments']:>10} {art['author_replies']:>10} {reply_rate:>9.1f}% {engage_rate:>9.2f}%")

    def velocity_milestone_correlation(self):
        """Corrélation Vitesse vs Événements."""
        conn = self.db.get_connection()
        print(f"\n⚡ VELOCITY PEAKS ↔ MILESTONE EVENTS")
        print("=" * 110)
        
        milestones = conn.execute("SELECT * FROM milestone_events WHERE article_id IS NOT NULL ORDER BY occurred_at DESC").fetchall()
        print(f"{'Event Type':<20} {'Article ID':<12} {'Time':<20} {'Before (v/h)':>15} {'After (v/h)':>15} {'Impact %':>10}")
        print("-" * 110)
        
        for m in milestones:
            v_before = self._calculate_period_velocity(m['article_id'], m['occurred_at'], -24)
            v_after = self._calculate_period_velocity(m['article_id'], m['occurred_at'], 24)
            
            # Correction division par zéro / Impact 100% si départ à 0
            impact = ((v_after - v_before) / v_before * 100) if v_before > 0 else (100.0 if v_after > 0 else 0.0)

            print(f"{m['event_type']:<20} {m['article_id']:<12} {m['occurred_at'][:19]:<20} {v_before:>15.2f} {v_after:>15.2f} {impact:>9.1f}%")

    def _calculate_period_velocity(self, article_id, event_time, hours_offset):
        """Calcule la vélocité sur 24h avant ou après."""
        conn = self.db.get_connection()
        t_event = datetime.fromisoformat(event_time.replace(' ', 'T').replace('Z', '+00:00'))
        t_target = t_event + timedelta(hours=hours_offset)
        
        # On prend les points dans la fenêtre
        t_min, t_max = (t_event, t_target) if hours_offset > 0 else (t_target, t_event)
        
        metrics = conn.execute("""
            SELECT views, collected_at FROM article_metrics 
            WHERE article_id = ? AND collected_at BETWEEN ? AND ?
            ORDER BY collected_at ASC
        """, (article_id, t_min.isoformat(), t_max.isoformat())).fetchall()
        
        if len(metrics) < 2: return 0.0
        
        v_diff = abs(metrics[-1]['views'] - metrics[0]['views'])
        return v_diff / abs(hours_offset)
    
    def weighted_follower_attribution(self, days=7):
        """
        Attribue les nouveaux followers au prorata du trafic (Share of Voice).
        Analyse les 'days' derniers jours.
        """
        conn = self.db.get_connection()
        
        # 1. Définir la période d'analyse
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        print(f"\n📈 WEIGHTED FOLLOWER ATTRIBUTION (Last {days} days)")
        print("=" * 110)
        
        # 2. Calculer le gain de followers total sur la période
        # On récupère le point le plus proche du début et de la fin
        f_start = conn.execute("""
            SELECT follower_count FROM follower_events 
            WHERE collected_at >= ? ORDER BY collected_at ASC LIMIT 1
        """, (start_time.isoformat(),)).fetchone()
        
        f_end = conn.execute("""
            SELECT follower_count FROM follower_events 
            WHERE collected_at <= ? ORDER BY collected_at DESC LIMIT 1
        """, (end_time.isoformat(),)).fetchone()
        
        if not f_start or not f_end:
            print("❌ Données de followers insuffisantes.")
            return

        total_gain = f_end['follower_count'] - f_start['follower_count']
        
        if total_gain <= 0:
            print(f"ℹ️ Aucun gain de followers sur les {days} derniers jours.")
            return

        # 3. Calculer les vues gagnées par CHAQUE article sur la période
        articles = self.db.get_all_active_articles()
        attribution_data = []
        global_traffic_gain = 0
        
        for art in articles:
            # Vues au début de la fenêtre
            v_start = conn.execute("""
                SELECT views FROM article_metrics 
                WHERE article_id = ? AND collected_at >= ? 
                ORDER BY collected_at ASC LIMIT 1
            """, (art['article_id'], start_time.isoformat())).fetchone()
            
            # Vues à la fin
            v_end = conn.execute("""
                SELECT views FROM article_metrics 
                WHERE article_id = ? AND collected_at <= ? 
                ORDER BY collected_at DESC LIMIT 1
            """, (art['article_id'], end_time.isoformat())).fetchone()
            
            if v_start and v_end:
                gain = v_end['views'] - v_start['views']
                if gain > 0:
                    attribution_data.append({
                        'title': art['title'],
                        'views_gain': gain
                    })
                    global_traffic_gain += gain

        if global_traffic_gain == 0:
            print("❌ Aucun trafic détecté sur la période.")
            return

        # 4. Affichage du rapport pondéré
        print(f"Total Gain: +{total_gain} followers | Total Traffic: {global_traffic_gain} views")
        print("-" * 110)
        print(f"{'Article':<50} {'Views':>12} {'Traffic %':>12} {'Followers':>15}")
        print("-" * 110)
        
        # Trier par gain de vues pour voir les "moteurs" en haut
        attribution_data.sort(key=lambda x: x['views_gain'], reverse=True)
        
        for item in attribution_data:
            share = (item['views_gain'] / global_traffic_gain)
            # On multiplie le gain total par la part de trafic de l'article
            attributed_followers = share * total_gain
            
            title = (item['title'][:47] + "...") if len(item['title']) > 50 else item['title']
            print(f"{title:<50} {item['views_gain']:>12,} {share:>11.1%} {attributed_followers:>15.1f}")

    def full_report(self):
        print("\n" + "=" * 110)
        print(" " * 38 + "📊 ADVANCED ANALYTICS REPORT")
        print("=" * 110)
        self.article_follower_correlation()
        self.comment_engagement_correlation()
        self.velocity_milestone_correlation()
        self.weighted_follower_attribution(days=7)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='devto_metrics.db')
    args = parser.parse_args()
    AdvancedAnalytics(args.db).full_report()

if __name__ == "__main__":
    main()