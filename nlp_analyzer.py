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
        """Vérifie et récupère les nouveaux commentaires ET le Markdown"""
        cursor = self.conn.cursor()
        
        # 1. On identifie les articles à vérifier
        cursor.execute("SELECT article_id, title FROM article_metrics GROUP BY article_id")
        articles = cursor.fetchall()
        
        for art in articles:
            # Récupération de la liste des IDs de commentaires depuis l'API
            res = requests.get(f"https://dev.to/api/comments?a_id={art['article_id']}")
            if res.status_code == 200:
                api_comments = res.json()
                
                for c in api_comments:
                    c_id = c.get('id_code')
                    # Si le commentaire n'existe pas du tout en base, on le récupère
                    cursor.execute("SELECT 1 FROM comments WHERE comment_id = ?", (c_id,))
                    if not cursor.fetchone():
                        print(f"✨ Nouveau commentaire trouvé sur '{art['title'][:30]}...'")
                        # Ici on appelle l'endpoint de détail pour avoir le Markdown direct
                        detail = requests.get(f"https://dev.to/api/comments/{c_id}").json()
                        
                        # Insertion complète (plus besoin de passer par le HTML)
                        cursor.execute("""
                            INSERT INTO comments (collected_at, comment_id, article_id, article_title, 
                            author_username, body_markdown, created_at)
                            VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?)
                        """, (c_id, art['article_id'], art['title'], 
                              detail.get('user', {}).get('username'), 
                              detail.get('body_markdown'), detail.get('created_at')))
                        self.conn.commit()

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

    def show_thematic_summary(self):
        """Regroupe les insights par article pour une vision stratégique"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT article_title, GROUP_CONCAT(body_markdown, ' || ') as all_comments
            FROM comments 
            WHERE author_username != 'pascal_cescato_692b7a8a20'
            GROUP BY article_title
        """)
        
        print(f"\n📑 SYNTHÈSE THÉMATIQUE PAR ARTICLE")
        print("="*100)
        
        for row in cursor.fetchall():
            doc = self.nlp(row['all_comments'])
            # On filtre les mots-clés techniques et les concepts fréquents
            keywords = [token.lemma_.lower() for token in doc 
                        if token.pos_ in ['NOUN', 'PROPN'] 
                        and not token.is_stop and len(token.text) > 2]
            
            # On prend les 5 plus fréquents
            from collections import Counter
            common = Counter(keywords).most_common(5)
            tags = ", ".join([word for word, count in common])
            
            print(f"\n📘 {row['article_title'][:60]}...")
            print(f"   🔝 Sujets chauds : {tags}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 nlp_analyzer.py VOTRE_CLE_API")
    else:
        analyzer = NLPAnalyzer(sys.argv[1])
        analyzer.sync_markdown_bodies()
        analyzer.extract_insights()