#!/usr/bin/env python3
"""
Analyser les réactions par type pour comprendre la logique de comptage
"""

import sqlite3

def analyze_reaction_types(db_path: str = "devto_metrics.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n" + "="*100)
    print("🔬 ANALYSE DES RÉACTIONS PAR TYPE")
    print("="*100)
    
    article_id = 2969205
    
    cursor.execute("""
        SELECT 
            title,
            published_at
        FROM article_metrics
        WHERE article_id = ?
        LIMIT 1
    """, (article_id,))
    
    info = cursor.fetchone()
    pub_date = info['published_at'][:10]
    
    print(f"\n📊 Article: {info['title'][:60]}")
    
    # Données depuis publication
    cursor.execute("""
        SELECT 
            date,
            reactions_total,
            reactions_like,
            reactions_unicorn,
            reactions_readinglist,
            comments_total
        FROM daily_analytics
        WHERE article_id = ?
        AND date >= ?
        ORDER BY date
    """, (article_id, pub_date))
    
    days = cursor.fetchall()
    
    print(f"\n📊 TOTAUX PAR TYPE (depuis publication):")
    
    sum_total = sum(d['reactions_total'] for d in days)
    sum_likes = sum(d['reactions_like'] for d in days)
    sum_unicorns = sum(d['reactions_unicorn'] for d in days)
    sum_bookmarks = sum(d['reactions_readinglist'] for d in days)
    
    print(f"   SUM(reactions_total):      {sum_total}")
    print(f"   SUM(reactions_like):       {sum_likes}")
    print(f"   SUM(reactions_unicorn):    {sum_unicorns}")
    print(f"   SUM(reactions_readinglist):{sum_bookmarks}")
    print(f"   -----------------------------------")
    print(f"   Breakdown sum:             {sum_likes + sum_unicorns + sum_bookmarks}")
    
    # Comparer avec lifetime
    cursor.execute("""
        SELECT reactions
        FROM article_metrics
        WHERE article_id = ?
        ORDER BY collected_at DESC
        LIMIT 1
    """, (article_id,))
    
    lifetime = cursor.fetchone()['reactions']
    
    print(f"\n   Lifetime (API):            {lifetime}")
    
    # Analyse
    breakdown_sum = sum_likes + sum_unicorns + sum_bookmarks
    
    print(f"\n🔍 OBSERVATIONS:")
    
    if sum_total == breakdown_sum:
        print(f"   ✅ reactions_total = somme du breakdown")
        print(f"      ({sum_total} = {sum_likes} + {sum_unicorns} + {sum_bookmarks})")
    else:
        print(f"   ⚠️  reactions_total ≠ somme du breakdown")
        print(f"      ({sum_total} ≠ {breakdown_sum})")
        print(f"      Différence: {sum_total - breakdown_sum}")
    
    if sum_total > lifetime:
        diff = sum_total - lifetime
        print(f"\n   ⚠️  SUM daily > Lifetime de {diff} réactions")
        print(f"      Hypothèses:")
        print(f"      1. Certaines réactions ont été retirées (unlikes)")
        print(f"      2. Il y a des doublons dans daily_analytics")
        print(f"      3. daily_analytics compte aussi les réactions 'hidden'")
    
    elif sum_total < lifetime:
        diff = lifetime - sum_total
        print(f"\n   ⚠️  SUM daily < Lifetime de {diff} réactions")
        print(f"      Hypothèses:")
        print(f"      1. Des réactions sont arrivées après la dernière collecte daily")
        print(f"      2. daily_analytics a un délai de synchronisation")
    
    # Test: regarder les derniers jours
    print(f"\n📅 DERNIERS JOURS (pour voir si c'est un délai):")
    print(f"   {'Date':<12} {'Total':>7} {'Likes':>7} {'🦄':>5} {'📖':>5}")
    print("   " + "-" * 45)
    
    for day in days[-10:]:
        print(f"   {day['date']:<12} {day['reactions_total']:>7} "
              f"{day['reactions_like']:>7} {day['reactions_unicorn']:>5} "
              f"{day['reactions_readinglist']:>5}")
    
    # Regarder si les derniers jours ont 0 réactions (délai de sync)
    last_days_reactions = sum(d['reactions_total'] for d in days[-3:])
    
    if last_days_reactions == 0:
        print(f"\n   ⚠️  Les 3 derniers jours ont 0 réactions")
        print(f"      → Possible délai de synchronisation de l'API")
    
    # SOLUTION PROBABLE
    print(f"\n" + "="*100)
    print("💡 SOLUTION PROBABLE")
    print("="*100)
    
    print(f"""
L'endpoint /api/analytics/historical retourne des données INCRÉMENTIELLES
(nouvelles réactions par jour), mais il y a un problème:

1. SUM(daily_analytics) = {sum_total} réactions
2. Lifetime (API)       = {lifetime} réactions
3. Différence           = {sum_total - lifetime} réactions

EXPLICATION LA PLUS PROBABLE:
L'endpoint analytics compte les réactions qui ont ensuite été retirées (unlikes).
Quand quelqu'un "unlike" un article, ça retire la réaction du total lifetime,
mais l'historique daily garde la trace de l'action initiale.

AUTRE POSSIBILITÉ:
Il y a un bug dans la façon dont vous collectez/stockez les données.
Peut-être des doublons lors de la collecte?

VÉRIFICATION À FAIRE:
Regardez dans votre code devto_tracker.py comment vous insérez les données
dans daily_analytics. Utilisez-vous INSERT OR REPLACE avec la bonne clé unique?
""")
    
    # Vérifier les clés uniques dans la table
    cursor.execute("PRAGMA table_info(daily_analytics)")
    columns = cursor.fetchall()
    
    cursor.execute("""
        SELECT sql FROM sqlite_master 
        WHERE type='table' AND name='daily_analytics'
    """)
    table_def = cursor.fetchone()
    
    print(f"\n🔍 STRUCTURE DE LA TABLE daily_analytics:")
    print(f"   {table_def['sql']}")
    
    # Vérifier s'il y a des doublons
    cursor.execute("""
        SELECT article_id, date, COUNT(*) as count
        FROM daily_analytics
        WHERE article_id = ?
        GROUP BY article_id, date
        HAVING count > 1
    """, (article_id,))
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"\n   ❌ DOUBLONS DÉTECTÉS!")
        for dup in duplicates:
            print(f"      Date {dup['date']} apparaît {dup['count']} fois")
    else:
        print(f"\n   ✅ Pas de doublons (UNIQUE constraint fonctionne)")
    
    conn.close()

if __name__ == "__main__":
    analyze_reaction_types()
