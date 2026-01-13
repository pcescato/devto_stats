#!/usr/bin/env python3
"""
Test potential hidden endpoints on DEV.to API
Usage: python3 endpoint_hunter.py YOUR_API_KEY
"""

import requests
import sys
import json
from datetime import datetime, timedelta

def test_endpoint(base_url, endpoint, headers, method="GET", params=None):
    """Test an endpoint and return status + sample response"""
    try:
        if method == "GET":
            response = requests.get(
                f"{base_url}{endpoint}",
                headers=headers,
                params=params,
                timeout=5
            )
        else:
            response = requests.post(
                f"{base_url}{endpoint}",
                headers=headers,
                json=params,
                timeout=5
            )
        
        status = response.status_code
        
        if status == 200:
            try:
                data = response.json()
                sample = json.dumps(data, indent=2)[:300]
                return "✅ FOUND", status, sample
            except:
                return "✅ FOUND (not JSON)", status, response.text[:200]
        elif status == 404:
            return "❌ Not found", status, None
        elif status == 401:
            return "🔒 Auth required", status, None
        elif status == 403:
            return "🚫 Forbidden", status, None
        elif status == 429:
            return "⏰ Rate limited", status, None
        else:
            return f"⚠️  Status {status}", status, None
            
    except requests.exceptions.Timeout:
        return "⏱️  Timeout", None, None
    except Exception as e:
        return f"❌ Error: {str(e)[:50]}", None, None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 endpoint_hunter.py YOUR_API_KEY")
        sys.exit(1)
    
    API_KEY = sys.argv[1]
    BASE_URL = "https://dev.to"
    
    headers = {
        "api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Endpoints to test
    endpoints = [
        # Known working (documented in Swagger)
        ("/api/articles/me/all", {}),
        ("/api/readinglist", {"per_page": 100}),
        ("/api/followers/users", {"sort": "-created_at", "per_page": 100}),
        ("/api/follows/tags", {}),
        
        # Known working (UNDOCUMENTED - our discovery!)
        ("/api/analytics/historical", {"start": "2026-01-01", "article_id": "3144468"}),
        
        # Potential analytics endpoints (not in Swagger)
        ("/api/dashboard", {}),
        ("/api/dashboard/stats", {}),
        ("/api/dashboard/analytics", {}),
        ("/api/stats", {}),
        ("/api/stats/summary", {}),
        ("/api/users/me/stats", {}),
        ("/api/users/me/analytics", {}),
        ("/api/users/me/dashboard", {}),
        
        # Article-specific analytics
        ("/api/articles/3144468/analytics", {}),
        ("/api/articles/3144468/stats", {}),
        ("/api/articles/3144468/traffic_sources", {}),
        
        # Analytics variations
        ("/api/analytics", {}),
        ("/api/analytics/summary", {}),
        ("/api/analytics/articles", {}),
        ("/api/analytics/followers", {}),
        ("/api/analytics/engagement", {}),
        ("/api/analytics/traffic", {}),
        
        # Reading & Activity
        ("/api/reading_stats", {}),
        ("/api/users/me/reading_stats", {}),
        ("/api/users/me/reading_history", {}),
        ("/api/activity", {}),
        ("/api/activity/stats", {}),
        
        # Followers
        ("/api/followers/analytics", {}),
        ("/api/followers/events", {}),
        ("/api/followers/recent", {}),
        ("/api/followers/stats", {}),
        
        # Reactions (try GET even though Swagger only shows POST)
        ("/api/reactions", {"reactable_type": "Article", "reactable_id": "3144468"}),
        ("/api/reactions/analytics", {}),
        ("/api/reactions/stats", {}),
        
        # Notifications
        ("/api/notifications/analytics", {}),
        ("/api/notifications/stats", {}),
        ("/api/notifications/unread_count", {}),
        
        # Internal API (may require different auth)
        ("/internal_api/analytics", {}),
        ("/internal_api/stats", {}),
        ("/internal_api/dashboard", {}),
        ("/internal_api/users/me/stats", {}),
        
        # Dashboard endpoints (browser interface)
        ("/dashboard/api/analytics", {}),
        ("/dashboard/api/stats", {}),
        ("/dashboard/analytics", {}),
        
        # Profile endpoints
        ("/api/profile/analytics", {}),
        ("/api/profile/stats", {}),
        
        # Organization endpoints (if applicable)
        ("/api/organizations/me", {}),
        ("/api/organizations/me/analytics", {}),
        
        # Comments analytics
        ("/api/comments/analytics", {}),
        ("/api/comments/stats", {}),
        
        # Tags analytics
        ("/api/tags/analytics", {}),
    ]
    
    print("="*80)
    print("🔍 DEV.TO API ENDPOINT HUNTER")
    print("="*80)
    print(f"\nTesting {len(endpoints)} potential endpoints...")
    print(f"Base URL: {BASE_URL}")
    print("\n" + "="*80 + "\n")
    
    found = []
    interesting = []
    
    for endpoint, params in endpoints:
        result, status, sample = test_endpoint(BASE_URL, endpoint, headers, params=params)
        
        print(f"{result:<25} {endpoint}")
        
        if status == 200:
            found.append(endpoint)
            if sample:
                print(f"  Sample: {sample}")
                interesting.append((endpoint, sample))
        
        print()
    
    print("="*80)
    print(f"\n📊 SUMMARY")
    print("="*80)
    print(f"Total endpoints tested: {len(endpoints)}")
    print(f"Working endpoints found: {len(found)}")
    
    if found:
        print("\n✅ WORKING ENDPOINTS:")
        for ep in found:
            print(f"  • {ep}")
    
    if interesting:
        print("\n🔥 INTERESTING RESPONSES (showing sample data):")
        for ep, sample in interesting[:5]:  # Show top 5
            print(f"\n  {ep}")
            print(f"  {sample[:200]}...")
    
    print("\n" + "="*80)
    print("\n💡 TIP: Try inspecting your DEV.to dashboard with Browser DevTools (F12)")
    print("   to see which endpoints the UI actually uses!")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
