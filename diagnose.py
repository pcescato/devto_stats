#!/usr/bin/env python3
"""
Diagnostiquer les collections d'un article spécifique
Pour comprendre d'où viennent les snapshots
"""

import sqlite3
from datetime import datetime

def diagnose_article_collections(article_id: int, db_path: str = "devto_metrics.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n" + "="*100)
    print(f"🔍 DIAGNOSTIC DES COLLECTIONS - Article #{article_id}")
    print("="*100)
    
    # Info de l'article
    cursor.execute("""
        SELECT title, published_at
        FROM article_metrics
        WHERE article_id = ?
        LIMIT 1
    """, (article_id,))
    
    info = cursor.fetchone()
    if not info:
        print(f"❌ Article {article_id} non trouvé")
        return
    
    print(f"\n📄 Article: {info['title']}")
    print(f"   Publié: {info['published_at']}")
    
    # TOUTES les collections pour cet article
    cursor.execute("""
        SELECT 
            collected_at,
            views,
            reactions,
            comments
        FROM article_metrics
        WHERE article_id = ?
        ORDER BY collected_at
    """, (article_id,))
    
    collections = cursor.fetchall()
    
    print(f"\n📊 HISTORIQUE DES COLLECTIONS ({len(collections)} snapshots):")
    print("-" * 100)
    print(f"{'#':<4} {'Collected At':<25} {'Views':<8} {'Δ Views':<10} {'Reactions':<12} {'Comments':<10} {'Time Since Prev':<20}")
    print("-" * 100)
    
    prev_time = None
    prev_views = None
    
    for i, coll in enumerate(collections, 1):
        collected_at = coll['collected_at']
        views = coll['views']
        reactions = coll['reactions']
        comments = coll['comments']
        
        # Calculer delta
        delta_views = views - prev_views if prev_views is not None else 0
        
        # Calculer temps depuis précédent
        if prev_time:
            try:
                curr_time = datetime.fromisoformat(collected_at.replace('Z', '+00:00'))
                prev_time_dt = datetime.fromisoformat(prev_time.replace('Z', '+00:00'))
                time_diff = curr_time - prev_time_dt
                hours_diff = time_diff.total_seconds() / 3600
                time_since = f"{int(hours_diff)}h{int((hours_diff % 1) * 60):02d}min"
            except:
                time_since = "N/A"
        else:
            time_since = "First"
        
        print(f"{i:<4} {collected_at:<25} {views:<8} {delta_views:+<10} {reactions:<12} {comments:<10} {time_since:<20}")
        
        prev_time = collected_at
        prev_views = views
    
    # Analyse des intervalles
    print("\n" + "="*100)
    print("📈 ANALYSE DES INTERVALLES")
    print("="*100)
    
    if len(collections) >= 2:
        intervals = []
        for i in range(1, len(collections)):
            try:
                curr = datetime.fromisoformat(collections[i]['collected_at'].replace('Z', '+00:00'))
                prev = datetime.fromisoformat(collections[i-1]['collected_at'].replace('Z', '+00:00'))
                interval_hours = (curr - prev).total_seconds() / 3600
                intervals.append(interval_hours)
            except:
                pass
        
        if intervals:
            print(f"\nIntervalles entre collections:")
            print(f"  Min:     {min(intervals):.1f}h")
            print(f"  Max:     {max(intervals):.1f}h")
            print(f"  Moyenne: {sum(intervals)/len(intervals):.1f}h")
            print(f"  Médiane: {sorted(intervals)[len(intervals)//2]:.1f}h")
            
            # Compter les intervalles
            from collections import Counter
            interval_ranges = []
            for h in intervals:
                if h < 1:
                    interval_ranges.append("< 1h")
                elif h < 2:
                    interval_ranges.append("1-2h")
                elif h < 4:
                    interval_ranges.append("2-4h")
                elif h < 6:
                    interval_ranges.append("4-6h")
                else:
                    interval_ranges.append("> 6h")
            
            counts = Counter(interval_ranges)
            print(f"\nDistribution des intervalles:")
            for range_name, count in sorted(counts.items()):
                print(f"  {range_name:<10} : {count} collections")
    
    # Vérifier si cron = 4h
    print("\n" + "="*100)
    print("🔍 VÉRIFICATION CRON")
    print("="*100)
    
    if intervals:
        avg_interval = sum(intervals) / len(intervals)
        
        if 3.5 <= avg_interval <= 4.5:
            print(f"✅ Intervalle moyen ~{avg_interval:.1f}h → Cron semble configuré pour 4h")
        elif 1.5 <= avg_interval <= 2.5:
            print(f"⚠️  Intervalle moyen ~{avg_interval:.1f}h → Cron semble configuré pour 2h")
        elif 0.5 <= avg_interval <= 1.5:
            print(f"⚠️  Intervalle moyen ~{avg_interval:.1f}h → Cron semble configuré pour 1h")
        else:
            print(f"❓ Intervalle moyen ~{avg_interval:.1f}h → Configuration cron non standard")
        
        # Détecter les anomalies
        anomalies = [h for h in intervals if h < 0.5 or (3 < h < 3.5 and avg_interval < 3)]
        if anomalies:
            print(f"\n⚠️  {len(anomalies)} intervalles anormaux détectés:")
            for anomaly in anomalies:
                print(f"    - {anomaly:.2f}h")
    
    # Explication du "Growth (over 3h)"
    print("\n" + "="*100)
    print("💡 EXPLICATION DU DASHBOARD")
    print("="*100)
    
    if len(collections) >= 2:
        first = collections[0]
        last = collections[-1]
        
        try:
            first_time = datetime.fromisoformat(first['collected_at'].replace('Z', '+00:00'))
            last_time = datetime.fromisoformat(last['collected_at'].replace('Z', '+00:00'))
            total_duration = last_time - first_time
            total_hours = total_duration.total_seconds() / 3600
            
            print(f"\nDashboard calcule:")
            print(f"  Première collection: {first['collected_at']}")
            print(f"  Dernière collection: {last['collected_at']}")
            print(f"  Durée totale:        {total_hours:.2f}h")
            print(f"  Views first→last:    {first['views']} → {last['views']} (+{last['views']-first['views']})")
            print(f"  Vélocité:            {(last['views']-first['views'])/total_hours:.2f} views/hour")
            
            print(f"\nCe qui donne l'affichage:")
            print(f"  📈 Growth (over {int(total_duration.days)}d {int(total_duration.seconds/3600)}h):")
            print(f"    +{last['views']-first['views']} views ({(last['views']-first['views'])/total_hours:.1f} views/hour)")
        except Exception as e:
            print(f"❌ Erreur calcul: {e}")
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        article_id = int(sys.argv[1])
    else:
        # Article récent par défaut
        article_id = 3163119  # "How I Cut My Cloud Run Bill by 96%"
    
    diagnose_article_collections(article_id)
