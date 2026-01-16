import os
import sqlite3
import spacy
from bs4 import BeautifulSoup
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()

class NLPAnalyzer:
    def __init__(self, db_path="devto_metrics.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.author_id = "pascal_cescato_692b7a8a20"
        self._setup_db()
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("❌ Erreur: Modèle spaCy 'en_core_web_sm' introuvable.")
            exit(1)

    def _setup_db(self):
        """Crée la table des résultats si elle n'existe pas"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comment_insights (
                comment_id TEXT PRIMARY KEY,
                sentiment_score REAL,
                mood TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (comment_id) REFERENCES comments (comment_id)
            )
        """)
        self.conn.commit()

    def clean_text(self, html):
        if not html: return ""
        soup = BeautifulSoup(html, "html.parser")
        for code in soup.find_all(['code', 'pre']):
            code.decompose()
        return soup.get_text(separator=' ').strip()

    def is_spam(self, text):
        spam_keywords = ['investigator', 'hack', 'whatsapp', 'spouse', 'cheating']
        t = text.lower()
        return any(k in t for k in spam_keywords) or ("@" in t and ".com" in t)

    def run(self):
        cursor = self.conn.cursor()
        
        # Sélection des commentaires non analysés
        query = """
            SELECT c.comment_id, c.article_title, c.body_html 
            FROM comments c
            LEFT JOIN comment_insights i ON c.comment_id = i.comment_id
            WHERE i.comment_id IS NULL AND c.author_username != ?
        """
        cursor.execute(query, (self.author_id,))
        rows = cursor.fetchall()

        if not rows:
            print("☕ Tout est à jour. Aucune nouvelle analyse nécessaire.")
            return

        print(f"🧠 Analyse de {len(rows)} nouveaux commentaires...")

        for row in rows:
            text = self.clean_text(row['body_html'])
            if text and not self.is_spam(text):
                score = TextBlob(text).sentiment.polarity
                mood = "🌟 Positif" if score > 0.15 else "😟 Négatif" if score < -0.1 else "😐 Neutre"
                
                cursor.execute("""
                    INSERT INTO comment_insights (comment_id, sentiment_score, mood)
                    VALUES (?, ?, ?)
                """, (row['comment_id'], score, mood))
        
        self.conn.commit()
        print("✅ Table comment_insights mise à jour.")

        # Affichage d'un petit résumé global pour le plaisir
        self.show_stats()

    def show_stats(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT mood, COUNT(*) as count FROM comment_insights GROUP BY mood")
        print("\n📊 ÉTAT GLOBAL DU SENTIMENT :")
        for row in cursor.fetchall():
            print(f"   {row['mood']} : {row['count']}")

if __name__ == "__main__":
    analyzer = NLPAnalyzer()
    analyzer.run()