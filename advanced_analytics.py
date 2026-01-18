#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Analytics (Version Finalisée) - Pascal Cescato Edition
- Attribution robuste des followers par calcul de delta temporel.
- Auto-détection de l'identifiant auteur pour isoler les réponses (Reply Rate).
- Analyse de l'engagement net des lecteurs.
- Corrélation entre pics de vélocité et événements milestones.
"""

import argparse
from datetime import datetime, timedelta
import statistics
from core.database import DatabaseManager

class AdvancedAnalytics:
    def __init__(self, db_path: str, author_username: str = "pascal_cescato_692b7a8a20"):
        self.db = DatabaseManager(db_path)
        self.author_username = author_username

    def article_follower_correlation(self):
        """
        Calcule le gain de followers réel en comparant les compteurs 
        au plus proche de la date de publication et 7 jours après.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
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
            
            # Point de données le plus proche de la publication (fenêtre +/- 6h)
            cursor.execute("""
                SELECT follower_count FROM follower_events 
                WHERE julianday(collected_at) BETWEEN julianday(?) - 0.25 AND julianday(?) + 0.25
                ORDER BY ABS(julianday(collected_at) - julianday(?)) ASC LIMIT 1
            """, (pub_date, pub_date, pub_date))
            start = cursor.fetchone()
            
            # Point de données le plus proche de J+7 (fenêtre +/- 6h)
            target_end = (datetime.fromisoformat(pub_date.replace('Z', '+00:00')) + timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT follower_count FROM follower_events 
                WHERE julianday(collected_at) BETWEEN julianday(?) - 0.25 AND julianday(?) + 0.25
                ORDER BY ABS(julianday(collected_at) - julianday(?)) ASC LIMIT 1
            """, (target_end, target_end, target_end))
            end = cursor.fetchone()

            if start and end:
                gain = end['follower_count'] - start['follower_count']
                # On n'affiche que les articles ayant un historique de followers cohérent
                if start['follower_count'] != end['follower_count'] or gain != 0:
                    title = (art['title'][:42] + "...") if len(art['title']) > 45 else art['title']
                    print(f"{title:<45} {pub_date[:10]:<12} {gain:>8} {start['follower_count']:>8} {end['follower_count']:>8} {art['total_views']:>8}")
        
        conn.close()

    def comment_engagement_correlation(self):
        """
        Analyse l'impact de tes interactions sur l'engagement global.
        Isole tes réponses du volume total de commentaires des lecteurs.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
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
        
        conn.close()


    def velocity_milestone_correlation(self):
        """
        Corrélation entre les pics de vélocité (vues/heure) et les événements milestones.
        Analyse si un title_change, staff_curated, ou autre événement a augmenté
        la moyenne des vues/heure dans les 24h qui ont suivi.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        print(f"\n⚡ VELOCITY PEAKS ↔ MILESTONE EVENTS")
        print("=" * 110)
        
        # Récupérer tous les événements avec un article_id
        cursor.execute("""
            SELECT 
                me.id,
                me.article_id,
                me.event_type,
                me.description,
                me.occurred_at
            FROM milestone_events me
            WHERE me.article_id IS NOT NULL
            ORDER BY me.occurred_at DESC
        """)
        
        milestones = cursor.fetchall()
        
        if not milestones:
            print("\n⭕ Aucun événement milestone avec article_id pour l'analyse")
            conn.close()
            return
        
        print(f"\n{'Event Type':<20} {'Article ID':<12} {'Time':<20} {'Before (v/h)':>15} {'After (v/h)':>15} {'Impact %':>10}")
        print("-" * 110)
        
        correlation_results = []
        
        for milestone in milestones:
            article_id = milestone['article_id']
            event_time = milestone['occurred_at']
            event_type = milestone['event_type'][:19]
            
            # Convertir l'heure de l'événement
            try:
                event_dt = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
            except:
                event_dt = datetime.strptime(event_time[:19], '%Y-%m-%d %H:%M:%S')
            
            # Fenêtre AVANT : 24h avant l'événement
            before_start = event_dt - timedelta(hours=24)
            before_end = event_dt
            
            # Fenêtre APRÈS : 24h après l'événement
            after_start = event_dt
            after_end = event_dt + timedelta(hours=24)
            
            # Récupérer les métriques AVANT
            cursor.execute("""
                SELECT 
                    views,
                    collected_at
                FROM article_metrics
                WHERE article_id = ?
                AND collected_at >= ?
                AND collected_at <= ?
                ORDER BY collected_at ASC
            """, (article_id, before_start.isoformat(), before_end.isoformat()))
            
            before_metrics = cursor.fetchall()
            
            # Récupérer les métriques APRÈS
            cursor.execute("""
                SELECT 
                    views,
                    collected_at
                FROM article_metrics
                WHERE article_id = ?
                AND collected_at >= ?
                AND collected_at <= ?
                ORDER BY collected_at ASC
            """, (article_id, after_start.isoformat(), after_end.isoformat()))
            
            after_metrics = cursor.fetchall()
            
            # Calculer les vélocités (vues/heure)
            before_velocity = self._calculate_velocity(before_metrics)
            after_velocity = self._calculate_velocity(after_metrics)
            
            # Calculer l'impact
            if before_velocity > 0:
                impact = ((after_velocity - before_velocity) / before_velocity) * 100
            else:
                impact = 0
            
            print(f"{event_type:<20} {article_id:<12} {event_time[:19]:<20} {before_velocity:>15.2f} {after_velocity:>15.2f} {impact:>9.1f}%")
            
            correlation_results.append({
                'event_type': milestone['event_type'],
                'impact': impact,
                'before': before_velocity,
                'after': after_velocity
            })
        
        # Analyse statistique par type d'événement
        if correlation_results:
            print(f"\n📊 IMPACT SUMMARY BY EVENT TYPE")
            print("-" * 110)
            
            event_types = {}
            for result in correlation_results:
                etype = result['event_type']
                if etype not in event_types:
                    event_types[etype] = []
                event_types[etype].append(result['impact'])
            
            print(f"{'Event Type':<30} {'Count':<8} {'Avg Impact %':<15} {'Min Impact %':<15} {'Max Impact %'}")
            print("-" * 110)
            
            for etype, impacts in sorted(event_types.items()):
                avg_impact = statistics.mean(impacts)
                min_impact = min(impacts)
                max_impact = max(impacts)
                
                print(f"{etype:<30} {len(impacts):<8} {avg_impact:>13.1f}% {min_impact:>13.1f}% {max_impact:>13.1f}%")
        
        conn.close()
    
    def _calculate_velocity(self, metrics):
        """
        Calcule la vélocité moyenne (vues/heure) à partir des métriques.
        Utilise les deltas pour éviter les recounts.
        """
        if len(metrics) < 2:
            return 0.0
        
        velocities = []
        
        for i in range(1, len(metrics)):
            current = metrics[i]
            previous = metrics[i-1]
            
            try:
                current_time = datetime.fromisoformat(current['collected_at'].replace('Z', '+00:00'))
                previous_time = datetime.fromisoformat(previous['collected_at'].replace('Z', '+00:00'))
            except:
                current_time = datetime.strptime(current['collected_at'][:19], '%Y-%m-%d %H:%M:%S')
                previous_time = datetime.strptime(previous['collected_at'][:19], '%Y-%m-%d %H:%M:%S')
            
            hours_diff = (current_time - previous_time).total_seconds() / 3600
            
            if hours_diff > 0:
                views_diff = current['views'] - previous['views']
                velocity = views_diff / hours_diff
                velocities.append(max(0, velocity))  # Éviter les valeurs négatives
        
        return statistics.mean(velocities) if velocities else 0.0

    def full_report(self):
        """Génère le rapport complet d'analyses avancées."""
        print("\n" + "=" * 110)
        print(" " * 38 + "📊 ADVANCED ANALYTICS REPORT")
        print("=" * 110)
        self.article_follower_correlation()
        self.comment_engagement_correlation()
        self.velocity_milestone_correlation()

def main():
    parser = argparse.ArgumentParser(description='Advanced Analytics - Pascal Edition')
    parser.add_argument('--db', default='devto_metrics.db', help='Chemin vers la base SQLite')
    parser.add_argument('--author', default='pascal_cescato_692b7a8a20', help='Ton username DEV.to')
    
    args = parser.parse_args()
    
    analytics = AdvancedAnalytics(args.db, args.author)
    analytics.full_report()

if __name__ == "__main__":
    main()