#!/usr/bin/env python3
"""
Script de correction des incohérences détectées
Usage: python3 fix_incoherences.py --db devto_metrics.db [--apply]
"""

import sqlite3
import argparse
from datetime import datetime

class IncoherenceFixer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.issues_found = []
    
    def connect(self):
        """Connect to database"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
    
    def diagnose(self):
        """Diagnose all issues"""
        self.connect()
        
        print("\n" + "="*80)
        print("🔍 DIAGNOSTIC DES INCOHÉRENCES")
        print("="*80)
        
        self.check_reaction_period_mismatch()
        self.check_traffic_calculation_errors()
        self.check_date_inconsistencies()
        
        print("\n" + "="*80)
        print(f"Total issues found: {len(self.issues_found)}")
        print("="*80)
    
    def check_reaction_period_mismatch(self):
        """Check for reaction data period mismatches"""
        cursor = self.conn.cursor()
        
        print("\n1️⃣  VÉRIFICATION: Réactions - Mélange de périodes")
        print("-" * 80)
        
        # Find articles where article_metrics reactions > daily_analytics reactions
        cursor.execute("""
            SELECT 
                am.article_id,
                am.title,
                MAX(am.reactions) as lifetime_reactions,
                MAX(da.reactions_total) as ninety_day_reactions,
                MAX(am.reactions) - COALESCE(MAX(da.reactions_total), 0) as missing_reactions,
                MIN(da.date) as earliest_daily_data,
                MAX(da.date) as latest_daily_data
            FROM article_metrics am
            LEFT JOIN daily_analytics da ON am.article_id = da.article_id
            GROUP BY am.article_id
            HAVING missing_reactions > 5
            ORDER BY missing_reactions DESC
        """)
        
        mismatches = cursor.fetchall()
        
        if mismatches:
            print(f"⚠️  {len(mismatches)} articles avec des réactions manquantes dans daily_analytics")
            print(f"\n{'Article ID':<12} {'Title':<40} {'Lifetime':<10} {'90-day':<10} {'Missing':<10}")
            print("-" * 80)
            
            for article in mismatches[:5]:  # Top 5
                title = article['title'][:37] + "..." if len(article['title']) > 40 else article['title']
                print(f"{article['article_id']:<12} {title:<40} "
                      f"{article['lifetime_reactions']:<10} "
                      f"{article['ninety_day_reactions'] or 0:<10} "
                      f"{article['missing_reactions']:<10}")
                
                self.issues_found.append({
                    'type': 'reaction_period_mismatch',
                    'article_id': article['article_id'],
                    'severity': 'high'
                })
            
            if len(mismatches) > 5:
                print(f"... and {len(mismatches) - 5} more articles")
        else:
            print("✅ Aucune incohérence détectée")
    
    def check_traffic_calculation_errors(self):
        """Check for traffic calculation errors"""
        cursor = self.conn.cursor()
        
        print("\n2️⃣  VÉRIFICATION: Calculs de trafic (views/week)")
        print("-" * 80)
        
        # Find articles where age > 90 days but traffic calc uses full age
        cursor.execute("""
            SELECT 
                r.article_id,
                am.title,
                am.published_at,
                julianday('now') - julianday(am.published_at) as age_days,
                SUM(r.count) as total_referrer_views,
                COUNT(DISTINCT r.collected_at) as data_collections
            FROM referrers r
            JOIN article_metrics am ON r.article_id = am.article_id
            WHERE am.published_at IS NOT NULL
            GROUP BY r.article_id
            HAVING age_days > 90
        """)
        
        traffic_issues = cursor.fetchall()
        
        if traffic_issues:
            print(f"⚠️  {len(traffic_issues)} articles avec calculs faussés (âge > 90 jours)")
            print("\n💡 Ces articles ont des vues Google calculées sur leur âge total,")
            print("   mais les données ne couvrent que 90 jours max.")
            
            for article in traffic_issues[:3]:
                title = article['title'][:50] if article['title'] else "N/A"
                print(f"\n   • {title}")
                print(f"     Age: {int(article['age_days'])} jours")
                print(f"     Données disponibles: ~90 jours max")
                print(f"     Impact: views/week sous-estimées de {(article['age_days'] / 90):.1f}x")
                
                self.issues_found.append({
                    'type': 'traffic_calculation_error',
                    'article_id': article['article_id'],
                    'severity': 'medium'
                })
        else:
            print("✅ Aucun problème détecté (ou pas de données referrers)")
    
    def check_date_inconsistencies(self):
        """Check for date format inconsistencies"""
        cursor = self.conn.cursor()
        
        print("\n3️⃣  VÉRIFICATION: Formats de dates")
        print("-" * 80)
        
        # Sample dates from different tables
        tables_dates = {}
        
        for table, date_col in [
            ('article_metrics', 'collected_at'),
            ('daily_analytics', 'collected_at'),
            ('follower_events', 'collected_at'),
            ('comments', 'collected_at')
        ]:
            cursor.execute(f"SELECT {date_col} FROM {table} LIMIT 1")
            row = cursor.fetchone()
            if row:
                tables_dates[table] = row[0]
        
        # Check consistency
        date_formats = {}
        for table, date_str in tables_dates.items():
            if 'T' in date_str:
                date_formats[table] = 'ISO with T'
            elif ' ' in date_str:
                date_formats[table] = 'SQL datetime'
            else:
                date_formats[table] = 'Unknown'
        
        unique_formats = set(date_formats.values())
        
        if len(unique_formats) > 1:
            print(f"⚠️  Formats de dates inconsistents:")
            for table, fmt in date_formats.items():
                print(f"   • {table:<20} → {fmt}")
            
            self.issues_found.append({
                'type': 'date_format_inconsistency',
                'severity': 'low'
            })
        else:
            print(f"✅ Format cohérent: {list(unique_formats)[0]}")
    
    def generate_fix_recommendations(self):
        """Generate specific fix recommendations"""
        print("\n" + "="*80)
        print("🔧 RECOMMANDATIONS DE CORRECTION")
        print("="*80)
        
        if not self.issues_found:
            print("\n✅ Aucune correction nécessaire!")
            return
        
        # Group by type
        by_type = {}
        for issue in self.issues_found:
            issue_type = issue['type']
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)
        
        # Recommendations per type
        print("\n📋 ACTIONS RECOMMANDÉES:")
        
        if 'reaction_period_mismatch' in by_type:
            count = len(by_type['reaction_period_mismatch'])
            print(f"\n1. Réactions manquantes ({count} articles):")
            print("   ✅ SOLUTION:")
            print("      - Modifier quality_analytics.py ligne 112-130")
            print("      - Utiliser UNIQUEMENT am.reactions (lifetime)")
            print("      - OU documenter clairement que breakdown = 90j seulement")
            print("\n   Code corrigé:")
            print("""
            cursor.execute(\"\"\"
                SELECT 
                    am.article_id,
                    am.title,
                    MAX(am.reactions) as total_reactions,  -- Lifetime (correct)
                    -- Breakdown disponible seulement sur 90j (optionnel)
                    MAX(da.reactions_like) as reactions_like_90d,
                    MAX(da.reactions_unicorn) as reactions_unicorn_90d,
                    MAX(da.reactions_readinglist) as reactions_bookmark_90d
                FROM article_metrics am
                LEFT JOIN daily_analytics da ON am.article_id = da.article_id
                WHERE am.reactions > 5
                GROUP BY am.article_id
                ORDER BY total_reactions DESC
                LIMIT 10
            \"\"\")
            """)
        
        if 'traffic_calculation_error' in by_type:
            count = len(by_type['traffic_calculation_error'])
            print(f"\n2. Calculs de trafic faussés ({count} articles):")
            print("   ✅ SOLUTION:")
            print("      - Modifier traffic_analytics.py ligne 177-186")
            print("      - Calculer views/week sur la période de données (90j max)")
            print("\n   Code corrigé:")
            print("""
            # Au lieu de:
            # views_per_week = (google_views / age_days) * 7
            
            # Utiliser:
            data_period_days = min(90, age_days)  # Données max sur 90 jours
            views_per_week = (google_views / data_period_days) * 7
            
            # Ou mieux: compter les jours réels de données
            cursor.execute(\"\"\"
                SELECT 
                    COUNT(DISTINCT date) as actual_days_with_data
                FROM daily_analytics
                WHERE article_id = ?
            \"\"\", (article_id,))
            actual_days = cursor.fetchone()['actual_days_with_data']
            views_per_week = (google_views / actual_days) * 7 if actual_days > 0 else 0
            """)
        
        if 'date_format_inconsistency' in by_type:
            print(f"\n3. Formats de dates inconsistants:")
            print("   ✅ SOLUTION:")
            print("      - Standardiser avec datetime.fromisoformat()")
            print("      - Créer une fonction utilitaire:")
            print("""
            def parse_api_datetime(date_str: str) -> datetime:
                \"\"\"Parse datetime from API (handles Z suffix and T separator)\"\"\"
                if not date_str:
                    return None
                # API returns ISO format with Z suffix
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            """)
    
    def apply_fixes(self):
        """Apply automatic fixes (if possible)"""
        print("\n" + "="*80)
        print("🔧 APPLICATION DES CORRECTIONS AUTOMATIQUES")
        print("="*80)
        print("\n⚠️  Cette fonction nécessiterait de modifier les fichiers Python.")
        print("    Pour l'instant, appliquez manuellement les corrections recommandées.")
        print("\n💡 Conseil: Créez une nouvelle branche Git avant de modifier le code!")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Diagnostic et correction des incohérences dans le code DEV.to Analytics"
    )
    
    parser.add_argument('--db', default='devto_metrics.db', 
                       help='Chemin vers la base de données')
    parser.add_argument('--apply', action='store_true',
                       help='Appliquer les corrections automatiques (pas encore implémenté)')
    
    args = parser.parse_args()
    
    fixer = IncoherenceFixer(args.db)
    
    try:
        fixer.diagnose()
        fixer.generate_fix_recommendations()
        
        if args.apply:
            fixer.apply_fixes()
    finally:
        fixer.close()


if __name__ == "__main__":
    main()