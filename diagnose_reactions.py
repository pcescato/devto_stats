#!/usr/bin/env python3
"""
Diagnostic script to examine reaction data in the database
"""
import sqlite3

conn = sqlite3.connect('devto_metrics.db')
cursor = conn.cursor()

print("="*80)
print("DIAGNOSTIC: Reaction Data Comparison")
print("="*80)

# Get all articles
cursor.execute("""
    SELECT DISTINCT article_id, title 
    FROM article_metrics 
    ORDER BY article_id
""")

articles = cursor.fetchall()

print(f"\nFound {len(articles)} articles\n")

for article_id, title in articles[:5]:  # First 5 articles
    print(f"\n{'='*80}")
    print(f"{title[:70]}")
    print(f"ID: {article_id}")
    print(f"{'='*80}")
    
    # 1. Latest data from article_metrics (public API)
    cursor.execute("""
        SELECT 
            reactions,
            comments,
            collected_at
        FROM article_metrics
        WHERE article_id = ?
        ORDER BY collected_at DESC
        LIMIT 1
    """, (article_id,))
    
    api_row = cursor.fetchone()
    if api_row:
        print(f"\n1. ARTICLE_METRICS (Public API - /api/articles/me/all):")
        print(f"   Latest collection: {api_row[2][:19]}")
        print(f"   Reactions:         {api_row[0]}")
        print(f"   Comments:          {api_row[1]}")
    
    # 2. Latest data from daily_analytics (hidden endpoint)
    cursor.execute("""
        SELECT 
            date,
            reactions_total,
            reactions_like,
            reactions_unicorn,
            reactions_readinglist,
            page_views
        FROM daily_analytics
        WHERE article_id = ?
        ORDER BY date DESC
        LIMIT 1
    """, (article_id,))
    
    hist_row = cursor.fetchone()
    if hist_row:
        print(f"\n2. DAILY_ANALYTICS (Hidden endpoint - /api/analytics/historical):")
        print(f"   Latest date:       {hist_row[0]}")
        print(f"   Total reactions:   {hist_row[1]}")
        print(f"   - Like:            {hist_row[2]}")
        print(f"   - Unicorn:         {hist_row[3]}")
        print(f"   - Bookmark:        {hist_row[4]}")
        print(f"   Page views:        {hist_row[5]}")
    else:
        print(f"\n2. DAILY_ANALYTICS: ❌ NO DATA")
    
    # 3. All daily_analytics entries
    cursor.execute("""
        SELECT COUNT(*), MIN(date), MAX(date)
        FROM daily_analytics
        WHERE article_id = ?
    """, (article_id,))
    
    count_row = cursor.fetchone()
    if count_row and count_row[0] > 0:
        print(f"\n3. DAILY_ANALYTICS HISTORY:")
        print(f"   Total entries:     {count_row[0]} days")
        print(f"   Date range:        {count_row[1]} to {count_row[2]}")
        
        # Show progression
        cursor.execute("""
            SELECT date, reactions_total, page_views
            FROM daily_analytics
            WHERE article_id = ?
            ORDER BY date DESC
            LIMIT 5
        """, (article_id,))
        
        print(f"\n   Recent progression:")
        print(f"   Date          Reactions  Views")
        print(f"   " + "-"*40)
        for row in cursor.fetchall():
            print(f"   {row[0]}    {row[1]:>5}      {row[2]:>5}")
    
    # 4. Comparison
    if api_row and hist_row:
        diff = api_row[0] - hist_row[1]
        print(f"\n4. COMPARISON:")
        print(f"   API public:        {api_row[0]} reactions")
        print(f"   Historical API:    {hist_row[1]} reactions")
        print(f"   Difference:        {diff} reactions")
        
        if diff > 0:
            print(f"   ⚠️  Historical endpoint is missing {diff} reactions!")
            print(f"   This might be because:")
            print(f"   - We only collected last 90 days")
            print(f"   - Reactions happened before collection started")
            print(f"   - Endpoint doesn't include all historical data")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}\n")

# Overall stats
cursor.execute("""
    SELECT 
        COUNT(DISTINCT article_id) as articles,
        SUM(CASE WHEN reactions_total IS NOT NULL THEN 1 ELSE 0 END) as with_hist_data
    FROM (
        SELECT DISTINCT article_id, MAX(reactions_total) as reactions_total
        FROM daily_analytics
        GROUP BY article_id
    )
""")

stats = cursor.fetchone()
print(f"Articles with daily_analytics data: {stats[1]} / {len(articles)}")

# Find discrepancies
cursor.execute("""
    SELECT 
        am.article_id,
        am.title,
        MAX(am.reactions) as api_reactions,
        MAX(da.reactions_total) as hist_reactions,
        MAX(am.reactions) - COALESCE(MAX(da.reactions_total), 0) as diff
    FROM article_metrics am
    LEFT JOIN daily_analytics da ON am.article_id = da.article_id
    GROUP BY am.article_id
    HAVING diff > 5
    ORDER BY diff DESC
    LIMIT 10
""")

discrepancies = cursor.fetchall()
if discrepancies:
    print(f"\nArticles with biggest discrepancies (>5 reactions):")
    print(f"{'Title':<50} {'API':>6} {'Hist':>6} {'Diff':>6}")
    print("-"*70)
    for row in discrepancies:
        title = row[1][:47] + "..." if len(row[1]) > 50 else row[1]
        print(f"{title:<50} {row[2]:>6} {row[3] or 0:>6} {row[4]:>6}")

conn.close()
