#!/usr/bin/env python3
"""Check actual database schema"""
import sqlite3

conn = sqlite3.connect('devto_metrics.db')
cursor = conn.cursor()

print("="*80)
print("DATABASE SCHEMA")
print("="*80)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\nTables found: {len(tables)}")
for table in tables:
    print(f"  • {table[0]}")

# Show article_metrics schema
print("\n" + "="*80)
print("ARTICLE_METRICS TABLE SCHEMA")
print("="*80)

cursor.execute("PRAGMA table_info(article_metrics)")
columns = cursor.fetchall()

print(f"\nColumns in article_metrics:")
for col in columns:
    print(f"  {col[1]:<30} {col[2]:<15} {'NOT NULL' if col[3] else ''}")

# Show sample data
print("\n" + "="*80)
print("SAMPLE DATA FROM ARTICLE_METRICS")
print("="*80)

cursor.execute("""
    SELECT * FROM article_metrics 
    ORDER BY collected_at DESC 
    LIMIT 1
""")

row = cursor.fetchone()
if row:
    cursor.execute("PRAGMA table_info(article_metrics)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print("\nLatest record:")
    for col_name, value in zip(columns, row):
        if value is not None:
            val_str = str(value)
            if len(val_str) > 60:
                val_str = val_str[:57] + "..."
            print(f"  {col_name:<30} = {val_str}")

# Show daily_analytics schema
print("\n" + "="*80)
print("DAILY_ANALYTICS TABLE SCHEMA")
print("="*80)

cursor.execute("PRAGMA table_info(daily_analytics)")
columns = cursor.fetchall()

print(f"\nColumns in daily_analytics:")
for col in columns:
    print(f"  {col[1]:<30} {col[2]:<15} {'NOT NULL' if col[3] else ''}")

conn.close()
