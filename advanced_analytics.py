#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta
import statistics
from core.database import DatabaseManager

class AdvancedAnalytics:
    def __init__(self, db_path: str, author_username: str = "pascal_cescato_692b7a8a20"):
        # On utilise ENFIN ton Manager
        self.db = DatabaseManager(db_path)
        self.author_username = author_username

    def article_follower_correlation(self):
        """Calcule le gain de followers avec la fenêtre de 6h (0.25 jour) suggérée par Copilot."""
        conn = self.db.get_connection()
        print("\n📊 ARTICLE → FOLLOWER CORRELATION (ROBUST DELTA)")
        print("=" * 110)
        
        # On récupère les articles
        articles = conn.execute("""
            SELECT article_id, title, published_at, MAX(views) as total_views
            FROM article_metrics WHERE published_at IS NOT NULL 
            GROUP BY article_id ORDER BY published_at DESC
        """).fetchall()

        print(f"{'Article':<45} {'Date':<12} {'Gain':>8} {'Start':>8} {'End':>8} {'Views':>8}")
        print("-" * 110)

        for art in articles:
            pub_date = art['published_at']
            # Fenêtre J+0 (+/- 6h)
            start = conn.execute("""
                SELECT follower_count FROM follower_events 
                WHERE julianday(collected_at) BETWEEN julianday(?) - 0.25 AND julianday(?) + 0.25
                ORDER BY ABS(julianday(collected_at) - julianday(?)) ASC LIMIT 1
            """, (pub_date, pub_date, pub_date)).fetchone()
            
            # Fenêtre J+7 (+/- 6h)
            target_end = (datetime.fromisoformat(pub_date.replace('Z', '+00:00')) + timedelta(days=7)).isoformat()
            end = conn.execute("""
                SELECT follower_count FROM follower_events 
                WHERE julianday(collected_at) BETWEEN julianday(?) - 0.25 AND julianday(?) + 0.25
                ORDER BY ABS(julianday(collected_at) - julianday(?)) ASC LIMIT 1
            """, (target_end, target_end, target_end)).fetchone()

            if start and end:
                gain = end['follower_count'] - start['follower_count']
                title = (art['title'][:42] + "...") if len(art['title']) > 45 else art['title']
                print(f"{title:<45} {pub_date[:10]:<12} {gain:>8} {start['follower_count']:>8} {end['follower_count']:>8} {art['total_views']:>8}")

    def velocity_milestone_correlation(self):
        """
        C'est ici que Copilot a failli. On lie les MILESTONES aux VUES.
        """
        conn = self.db.get_connection()
        print(f"\n⚡ VELOCITY PEAKS ↔ MILESTONE EVENTS")
        print("=" * 110)
        
        milestones = conn.execute("""
            SELECT article_id, event_type, occurred_at, description 
            FROM milestone_events WHERE article_id IS NOT NULL 
            ORDER BY occurred_at DESC
        """).fetchall()
        
        print(f"{'Event Type':<20} {'Article ID':<12} {'Time':<20} {'Before (v/h)':>15} {'After (v/h)':>15} {'Impact %':>10}")
        print("-" * 110)
        
        for m in milestones:
            # On réutilise la même logique de fenêtre pour la vélocité
            v_before = self._get_avg_velocity(m['article_id'], m['occurred_at'], offset_hours=-24)
            v_after = self._get_avg_velocity(m['article_id'], m['occurred_at'], offset_hours=24)
            
            impact = ((v_after - v_before) / v_before * 100) if v_before > 0 else 0.0
            if v_before == 0 and v_after > 0: impact = 100.0 # Nouveau départ

            print(f"{m['event_type']:<20} {m['article_id']:<12} {m['occurred_at'][:19]:<20} {v_before:>15.2f} {v_after:>15.2f} {impact:>9.1f}%")

    def _get_avg_velocity(self, article_id, event_time, offset_hours):
        """Calcule la vélocité moyenne sur une période donnée."""
        conn = self.db.get_connection()
        # Calcul de la plage
        t1 = event_time
        t2 = (datetime.fromisoformat(event_time.replace(' ', 'T')) + timedelta(hours=offset_hours)).isoformat()
        
        # On prend le premier et le dernier point de la période
        points = conn.execute("""
            SELECT views, collected_at FROM article_metrics 
            WHERE article_id = ? AND julianday(collected_at) BETWEEN julianday(?) - 0.5 AND julianday(?) + 0.5
            ORDER BY collected_at ASC
        """, (article_id, t1, t2)).fetchall()
        
        if len(points) < 2: return 0.0
        
        views_diff = abs(points[-1]['views'] - points[0]['views'])
        return views_diff / abs(offset_hours)

    def full_report(self):
        self.article_follower_correlation()
        self.velocity_milestone_correlation()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='devto_metrics.db')
    args = parser.parse_args()
    AdvancedAnalytics(args.db).full_report()

if __name__ == "__main__":
    main()