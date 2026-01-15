# 📊 Quality Analytics - Read Time & Reaction Breakdown

## ⚠️ IMPORTANT: Data Is Cumulative

The `/api/analytics/historical` endpoint returns **cumulative totals** per day, 
not daily increments. 

**What this means:**
- `total_read_time_seconds` = total since publication (cumulative)
- `page_views.total` = total since publication (cumulative)
- `reactions_total` = total since publication (cumulative)

**Our code uses `MAX()` to get the latest cumul, not `SUM()` which would 
over-count by adding all snapshots together.**

See `BUG_FIX_DOUBLE_COUNTING.md` for details on the fix.

---

## 🔥 New Feature: Daily Analytics

We discovered an **undocumented endpoint** in DEV.to's API that reveals much richer data:

```
GET /api/analytics/historical?start=YYYY-MM-DD&article_id=ID
```

This endpoint provides:
- ✅ **Daily breakdown** of views (not just totals)
- ✅ **Average read time** per day (how long people actually read)
- ✅ **Total read time** (total hours of reading created)
- ✅ **Reaction breakdown** (likes vs unicorns vs bookmarks)
- ✅ **Comment counts** per day

## 🚀 Quick Start

### Step 1: Collect Daily Analytics

```bash
# First time: collect last 90 days for all articles
python3 devto_tracker.py --api-key YOUR_KEY --collect-daily

# This will take a few minutes (0.5s delay per article to avoid rate limiting)
```

### Step 2: View Quality Dashboard

```bash
# Full dashboard
python3 quality_analytics.py

# Or specific analyses
python3 quality_analytics.py --read-time
python3 quality_analytics.py --reactions
python3 quality_analytics.py --long-tail
python3 quality_analytics.py --quality

# Daily breakdown for specific article
python3 quality_analytics.py --article 3144468
```

## 📊 What You Get

### 1. Read Time Analysis

Shows which articles people actually READ (vs just scroll):

```
📖 READ TIME ANALYSIS (Top 10)
----------------------------------------------------------------------------------------------------
Title                                              Length  Avg Read  Completion  Total Hours
----------------------------------------------------------------------------------------------------
Actually Agile: Against Performance Theater...          8m     270s      56.3%        14.0h
Beyond the Linear CV                                    7m     175s      41.7%        30.7h
Respiration                                             6m     180s      50.0%         5.5h
```

**Key Metrics:**
- **Avg Read**: Average time spent reading (seconds)
- **Completion**: What % of the article they read (avg_read / article_length)
- **Total Hours**: Total reading time created (e.g., 30.7h = 30+ hours of value)

### 2. Reaction Breakdown

See WHICH reactions people give (not just totals):

```
❤️ REACTION BREAKDOWN (Top 10)
----------------------------------------------------------------------------------------------------
Title                                              Likes   Unicorn   Bookmark    Total
----------------------------------------------------------------------------------------------------
Actually Agile                                        30        12          8       52
Beyond the Linear CV                                  15         2          5       25
```

**Pattern Analysis:**
```
💡 Reaction Patterns:
  • High Unicorn (Excitement): 3 articles
  • High Bookmark (Value): 5 articles
  • Standard (Likes): 14 articles
```

**What it means:**
- **High Unicorn** → People are EXCITED (controversial, inspiring)
- **High Bookmark** → People want to read later (valuable, reference material)
- **Standard Likes** → General appreciation

### 3. Long-Tail Champions

Identifies articles that keep getting views months after publication:

```
🌟 LONG-TAIL CHAMPIONS (Recent views on old articles)
----------------------------------------------------------------------------------------------------
Title                                              Age     Last 30d     30-90d     Trend
----------------------------------------------------------------------------------------------------
Actually Agile                                     90d          120         95      +26%
AgentKit                                           73d           65         82      -21%
```

**This reveals:**
- Which articles have SEO power (search engine traffic)
- Which topics have evergreen value
- Which articles to update/promote

### 4. Quality Scores

Combines read completion + engagement into a single score:

```
⭐ QUALITY SCORES (Completion + Engagement)
----------------------------------------------------------------------------------------------------
Title                                              Quality   Read %   Engage %
----------------------------------------------------------------------------------------------------
Beyond the Linear CV                                  58.3    41.7%       3.4%
Actually Agile                                        44.8    56.3%       4.0%
Respiration                                           43.5    50.0%       9.0%
```

**Formula:** `Quality Score = (Read Completion × 70%) + (Engagement Rate × 30%)`

**High quality** = People read it fully AND engage with it

## 🔍 Detailed Analysis

### Per-Article Daily Breakdown

```bash
python3 quality_analytics.py --article 3144468
```

Output:
```
📊 DAILY BREAKDOWN: Beyond the Linear CV
Published: 2026-01-04
Length: 7 minutes

Date         Views   Read(s)   Likes   🦄   📖   💬
--------------------------------------------------------------------
2026-01-08      13       61       0    0    1    0
2026-01-07     120      213       1    0    2    2
2026-01-06     211      171       1    0    3    2
2026-01-05     631      175       6    1    1    2
2026-01-04     274      121       6    2    1    9
```

**This shows:**
- When views peaked (J+1: 631 views)
- When read time increased (J+3: 213s avg = people reading more carefully)
- Reaction types by day (bookmarks on J+2 = people saving for later)

## 💡 Insights You Can Extract

### 1. Read Time = Quality Proxy

```
Articles with high avg read time (>50% completion):
→ People find them valuable
→ Google likely ranks them higher (dwell time)
→ Worth updating and promoting

Articles with low avg read time (<20% completion):
→ Misleading title?
→ Content doesn't match expectation?
→ Too long/verbose?
```

### 2. Reaction Patterns Tell Stories

```
Unicorns = Excitement/Agreement
→ Controversial opinions
→ Inspiring stories
→ "Yes! Exactly!"

Bookmarks = Reference Value
→ Technical how-tos
→ Resource lists
→ "I'll need this later"

Pure Likes = General appreciation
→ Entertaining
→ Well-written
→ But not life-changing
```

### 3. Long-Tail Reveals SEO Winners

```
Articles with views 3+ months after publication:
→ Ranking for search terms
→ Evergreen topics
→ Worth maintaining/updating

Update strategy:
1. Find your long-tail champions
2. Add recent examples/updates
3. Improve SEO (meta description, keywords)
4. Watch views climb again
```

## ⚙️ Automation

### Collect Daily Analytics Regularly

Add to your cron:
```bash
# Once per day (recommended)
0 3 * * * cd /root/devstats && python3 devto_tracker.py --api-key YOUR_KEY --collect-daily >> logs/daily_analytics.log 2>&1
```

**Note:** This is slower than regular collection (0.5s per article) so run it separately.

### Combined Collection

Or add to your regular collection by uncommenting in `devto_tracker.py`:
```python
def collect_snapshot(self):
    # ...
    # 5. Daily Analytics (uncomment to enable)
    self._fetch_and_save_daily_analytics(articles, timestamp)
```

## 📈 Use Cases

### 1. Content Strategy
"Which articles create the most value (read time)?"
→ Focus on similar topics

### 2. Title Optimization
"Why do people click but not read?"
→ Title doesn't match content

### 3. SEO Strategy
"Which articles have long-tail power?"
→ Invest in updating those

### 4. Engagement Analysis
"Are people excited or just appreciative?"
→ Unicorns vs Likes tells you

### 5. Quality Metrics
"Which articles are truly high quality?"
→ Quality Score ranks by completion + engagement

## ⚠️ Important Notes

### About the Endpoint

This endpoint is **undocumented** and could:
- Change without notice
- Have different rate limits
- Be removed

**Recommendations:**
- Collect data regularly (you can't go back in time)
- Don't abuse (0.5s delay between requests)
- Have a backup strategy

### About the Data

**"follows_total"** in the response seems to be:
- Your total follower count (cumulative)
- NOT followers gained from that specific article
- Don't use for article-to-follower correlation

**Read time accuracy:**
- Measures tab focus time
- Long read times (>10min on 5min article) = person had tab open while doing something else
- Still valuable as it shows which content makes people pause and reflect

## 🚀 Next Steps

1. **Collect your first 90 days:**
   ```bash
   python3 devto_tracker.py --api-key YOUR_KEY --collect-daily
   ```

2. **Explore the dashboard:**
   ```bash
   python3 quality_analytics.py
   ```

3. **Analyze your best article:**
   ```bash
   python3 quality_analytics.py --article YOUR_BEST_ARTICLE_ID
   ```

4. **Compare with your worst:**
   ```bash
   python3 quality_analytics.py --article YOUR_WORST_ARTICLE_ID
   ```

5. **Find patterns!**

---

**This data changes everything.** It's not about views anymore—it's about creating value.

And now you can measure it.