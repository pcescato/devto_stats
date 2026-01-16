#!/usr/bin/env python3
import sqlite3
import requests
import spacy
import time
import sys
from collections import Counter
from textblob import TextBlob

class NLPAnalyzer:
    def __init__(self, api_key, db_path="devto_metrics.db"):
        self.api_key = api_key
        self.headers = {"api-key": api_key}
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.author_id = "pascal_cescato_692b7a8a20"
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("❌ Erreur : Modèle spaCy introuvable. Fais : python3 -m spacy download en_core_web_sm")
            sys.exit(1)

    def sync_all(self):
        """Récupère les nouveaux commentaires et assure que le Markdown est là"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT article_id, title FROM article_metrics GROUP BY article_id")
        articles = cursor.fetchall()

        print(f"🔄 Vérification des nouveaux commentaires sur {len(articles)} articles...")
        for art in articles:
            res = requests.get(f"https://dev.to/api/comments?a_id={art['article_id']}")
            if res.status_code == 200:
                for c in res.json():
                    c_id = c.get('id_code')
                    cursor.execute("SELECT body_markdown FROM comments WHERE comment_id = ?", (c_id,))
                    row = cursor.fetchone()
                    
                    if not row or not row['body_markdown']:
                        print(f"  ✨ Récupération Markdown pour comment {c_id} sur '{art['title'][:30]}...'")
                        detail = requests.get(f"https://dev.to/api/comments/{c_id}").json()
                        md = detail.get('body_markdown', '')
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO comments 
                            (collected_at, comment_id, article_id, article_title, author_username, body_markdown, created_at)
                            VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?)
                        """, (c_id, art['article_id'], art['title'], 
                              detail.get('user', {}).get('username'), md, detail.get('created_at')))
                        self.conn.commit()
                        time.sleep(0.2)

    def analyze(self):
        """Analyse sémantique et sentimentale"""
        cursor = self.conn.cursor()
        # On récupère tout ce qui n'est pas de toi
        cursor.execute("SELECT article_title, body_markdown FROM comments WHERE author_username != ?", (self.author_id,))
        rows = cursor.fetchall()

        print(f"\n🧠 ANALYSE DE L'AUDIENCE ({len(rows)} commentaires)")
        print("="*100)

        # Regroupement par article pour la synthèse
        by_article = {}
        for row in rows:
            title = row['article_title']
            if title not in by_article: by_article[title] = []
            by_article[title].append(row['body_markdown'])

        for title, texts in by_article.items():
            full_text = " ".join(texts)
            doc = self.nlp(full_text)
            
            # 1. Sentiment (Polarité de -1 à 1)
            sentiment = TextBlob(full_text).sentiment.polarity
            mood = "😊 Positif" if sentiment > 0.1 else "😐 Neutre" if sentiment > -0.1 else "😟 Négatif"
            
            # 2. Mots-clés (Noms communs les plus fréquents)
            keywords = [token.lemma_.lower() for token in doc 
                        if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop and len(token.text) > 2]
            common = [w for w, c in Counter(keywords).most_common(5)]

            print(f"\n📘 {title[:70]}...")
            print(f"   🎭 Ambiance : {mood} ({sentiment:.2f})")
            print(f"   🔝 Sujets : {', '.join(common)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nlp_analyzer.py VOTRE_CLE_API")
    else:
        ana = NLPAnalyzer(sys.argv[1])
        ana.sync_all()
        ana.analyze()