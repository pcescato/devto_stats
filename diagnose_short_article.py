#!/usr/bin/env python3
"""
Diagnostic: Pourquoi certains articles ont si peu de contenu ?
"""

import sqlite3
import requests
import sys

def check_article_content(article_id: int, api_key: str, db_path: str = "devto_metrics.db"):
    """Compare ce qui est en DB vs ce que l'API retourne"""
    
    print("="*80)
    print(f"🔍 DIAGNOSTIC ARTICLE #{article_id}")
    print("="*80)
    
    # 1. Ce qui est en DB
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            ac.word_count,
            ac.char_count,
            ac.code_blocks_count,
            LENGTH(ac.body_markdown) as markdown_length,
            am.title
        FROM article_content ac
        JOIN article_metrics am ON ac.article_id = am.article_id
        WHERE ac.article_id = ?
    """, (article_id,))
    
    db_row = cursor.fetchone()
    
    if db_row:
        print(f"\n📊 EN BASE DE DONNÉES:")
        print(f"   Title:        {db_row['title']}")
        print(f"   Word count:   {db_row['word_count']}")
        print(f"   Char count:   {db_row['char_count']}")
        print(f"   Code blocks:  {db_row['code_blocks_count']}")
        print(f"   Markdown len: {db_row['markdown_length']} bytes")
        
        # Afficher un extrait du markdown
        cursor.execute("""
            SELECT body_markdown
            FROM article_content
            WHERE article_id = ?
        """, (article_id,))
        
        markdown = cursor.fetchone()['body_markdown']
        print(f"\n📝 EXTRAIT DU MARKDOWN (premiers 500 chars):")
        print("-"*80)
        print(markdown[:500])
        print("-"*80)
    else:
        print(f"\n❌ Article {article_id} pas en base")
        conn.close()
        return
    
    # 2. Ce que l'API retourne
    print(f"\n🌐 APPEL API:")
    
    response = requests.get(
        f"https://dev.to/api/articles/{article_id}",
        headers={"api-key": api_key}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        markdown_api = data.get('body_markdown', '')
        html_api = data.get('body_html', '')
        
        print(f"   Status:           {response.status_code} ✅")
        print(f"   Markdown length:  {len(markdown_api)} bytes")
        print(f"   HTML length:      {len(html_api)} bytes")
        
        # Comparer
        print(f"\n🔍 COMPARAISON:")
        if len(markdown_api) == db_row['markdown_length']:
            print(f"   ✅ Markdown identique ({len(markdown_api)} bytes)")
        else:
            print(f"   ⚠️  DIFFÉRENCE!")
            print(f"      DB:  {db_row['markdown_length']} bytes")
            print(f"      API: {len(markdown_api)} bytes")
            print(f"      Delta: {len(markdown_api) - db_row['markdown_length']} bytes")
        
        # Afficher extrait de l'API
        print(f"\n📝 EXTRAIT DE L'API (premiers 500 chars):")
        print("-"*80)
        print(markdown_api[:500])
        print("-"*80)
        
        # Compter mots manuellement
        import re
        code_pattern = r'```(\w+)?\n(.*?)```'
        text_without_code = re.sub(code_pattern, '', markdown_api, flags=re.DOTALL)
        words_api = text_without_code.split()
        
        print(f"\n🔢 RECOMPTE MANUEL:")
        print(f"   Mots (sans code): {len(words_api)}")
        print(f"   DB word_count:    {db_row['word_count']}")
        
        if len(words_api) != db_row['word_count']:
            print(f"   ⚠️  DIFFÉRENCE: {len(words_api) - db_row['word_count']} mots")
        
        # Vérifier s'il y a du contenu canonique
        if 'canonical_url' in data and data['canonical_url']:
            print(f"\n🔗 CANONICAL URL DÉTECTÉE:")
            print(f"   {data['canonical_url']}")
            print(f"   ⚠️  Cet article est peut-être un lien vers un article externe!")
    else:
        print(f"   Status: {response.status_code} ❌")
    
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 diagnose_short_article.py ARTICLE_ID API_KEY")
        print("\nExemple:")
        print("  python3 diagnose_short_article.py 3119827 YOUR_KEY")
        sys.exit(1)
    
    article_id = int(sys.argv[1])
    api_key = sys.argv[2]
    
    check_article_content(article_id, api_key)
