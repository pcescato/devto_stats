import sqlite3
import spacy
from bs4 import BeautifulSoup
from textblob import TextBlob
from collections import Counter

class HTMLNLPAnalyzer:
    def __init__(self, db_path="devto_metrics.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.author_id = "pascal_cescato_692b7a8a20"
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Fais d'abord : python3 -m spacy download en_core_web_sm")

    def clean_text(self, html):
        """Transforme le HTML en texte brut propre"""
        if not html: return ""
        soup = BeautifulSoup(html, "html.parser")
        # On enlève les balises de code pour ne pas polluer l'analyse sémantique
        for code in soup.find_all(['code', 'pre']):
            code.decompose()
        return soup.get_text(separator=' ')

    def run(self):
        cursor = self.conn.cursor()
        # On récupère les commentaires des lecteurs (body_html est déjà là !)
        cursor.execute("SELECT article_title, body_html FROM comments WHERE author_username != ?", (self.author_id,))
        rows = cursor.fetchall()

        by_article = {}
        for row in rows:
            title = row['article_title']
            text = self.clean_text(row['body_html'])
            if text:
                if title not in by_article: by_article[title] = []
                by_article[title].append(text)

        print(f"\n🧠 ANALYSE SÉMANTIQUE (Source: HTML Cleaned)")
        print("="*100)

        for title, texts in by_article.items():
            full_text = " ".join(texts)
            doc = self.nlp(full_text)
            
            # Sentiment
            sentiment = TextBlob(full_text).sentiment.polarity
            mood = "🌟 Positif" if sentiment > 0.1 else "😐 Neutre"
            
            # Mots-clés (Noms et Adjectifs)
            keywords = [t.lemma_.lower() for t in doc 
                        if t.pos_ in ['NOUN', 'ADJ'] and not t.is_stop and len(t.text) > 3]
            common = [f"{w} ({c})" for w, c in Counter(keywords).most_common(6)]

            print(f"\n📘 {title[:70]}...")
            print(f"   🎭 Sentiment : {mood} ({sentiment:.3f})")
            print(f"   🔝 Concepts  : {', '.join(common)}")

if __name__ == "__main__":
    analyzer = HTMLNLPAnalyzer()
    analyzer.run()