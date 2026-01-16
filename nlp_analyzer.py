import sqlite3
import spacy
from bs4 import BeautifulSoup
from textblob import TextBlob
from collections import Counter
import sys

class NLPAnalyzer:
    def __init__(self, db_path="devto_metrics.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.author_id = "pascal_cescato_692b7a8a20"
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Erreur: Modèle spaCy manquant.")
            sys.exit(1)

    def clean_text(self, html):
        if not html: return ""
        soup = BeautifulSoup(html, "html.parser")
        # On vire le code pour ne pas fausser l'analyse sémantique
        for code in soup.find_all(['code', 'pre']):
            code.decompose()
        return soup.get_text(separator=' ')

    def run(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT article_title, body_html 
            FROM comments 
            WHERE author_username != ?
        """, (self.author_id,))
        rows = cursor.fetchall()

        by_article = {}
        for row in rows:
            title = row['article_title']
            text = self.clean_text(row['body_html'])
            
            # Filtre anti-spam basique : on ignore les caractères non-latins (comme ton spam iranien)
            if text and any(ord(c) > 127 for c in text) and "ع" in text: 
                continue

            if text and len(text.split()) > 3:
                if title not in by_article: by_article[title] = []
                by_article[title].append(text)

        print(f"\n🧠 INSIGHTS SÉMANTIQUES ({len(by_article)} Articles)")
        print("="*100)

        for title, texts in by_article.items():
            full_text = " ".join(texts)
            doc = self.nlp(full_text)
            
            sentiment = TextBlob(full_text).sentiment.polarity
            
            # Extraction des noms porteurs de sens
            keywords = [t.text.lower() for t in doc 
                        if not t.is_stop and t.is_alpha and len(t.text) > 3 
                        and t.pos_ in ['NOUN', 'PROPN', 'ADJ']]
            
            common = [f"{w} ({c})" for w, c in Counter(keywords).most_common(6)]
            mood = "🌟 Positif" if sentiment > 0.15 else "😟 Négatif" if sentiment < -0.1 else "😐 Neutre"
            
            print(f"\n📘 {title[:75]}")
            print(f"   🎭 Sentiment : {mood} ({sentiment:.3f})")
            print(f"   🔝 Concepts  : {', '.join(common)}")

if __name__ == "__main__":
    analyzer = NLPAnalyzer()
    analyzer.run()