#!/usr/bin/env python3
import sqlite3
import requests
import spacy
import time

class NLPAnalyzer:
    def __init__(self, api_key, db_path="devto_metrics.db"):
        self.api_key = api_key
        self.headers = {"api-key": api_key}
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Chargement du modèle spaCy (Anglais par défaut pour la tech)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Exécute d'abord : python3 -m spacy download en_core_web_sm")

    def sync_markdown_bodies(self):
        """Récupère le Markdown depuis l'API pour les commentaires qui ne l'ont pas encore"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT comment_id FROM comments WHERE body_markdown IS NULL OR body_markdown = ''")
        rows = cursor.fetchall()
        
        if not rows:
            return

        print(f"🔄 Synchronisation de {len(rows)} commentaires (Markdown)...")
        for row in rows:
            c_id = row['comment_id']
            res = requests.get(f"https://dev.to/api/comments/{c_id}")
            if res.status_code == 200:
                md = res.json().get('body_markdown', '')
                cursor.execute("UPDATE comments SET body_markdown = ? WHERE comment_id = ?", (md, c_id))
                self.conn.commit()
                time.sleep(0.2) # Courtoisie API

    def extract_insights(self):
        """Analyse sémantique des commentaires des lecteurs"""
        cursor = self.conn.cursor()
        # On exclut tes propres commentaires pour l'analyse d'audience
        cursor.execute("""
            SELECT article_title, body_markdown 
            FROM comments 
            WHERE author_username != 'pascal_cescato_692b7a8a20' 
            AND body_markdown IS NOT NULL
        """)
        
        print(f"\n🧠 INSIGHTS SÉMANTIQUES (Lecteurs)")
        print("="*100)
        
        for row in cursor.fetchall():
            doc = self.nlp(row['body_markdown'])
            # Extraction des noms propres et entités techniques (ORG/PRODUCT)
            tech_entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT"]]
            
            if tech_entities:
                print(f"\nArt: {row['article_title'][:50]}...")
                print(f"  └ Tags détectés: {', '.join(set(tech_entities))}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 nlp_analyzer.py VOTRE_CLE_API")
    else:
        analyzer = NLPAnalyzer(sys.argv[1])
        analyzer.sync_markdown_bodies()
        analyzer.extract_insights()