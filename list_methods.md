# DEV.to Analytics Toolkit - Available Methods

Complete reference guide for all scripts and their available commands.

---

## 📊 Main Dashboard

### `dashboard.py`
Display your complete personal dashboard with latest metrics, trends, and insights.

```bash
# Show full dashboard (default)
python3 dashboard.py

# Specify custom database path
python3 dashboard.py --db path/to/database.db
```

**What it shows:**
- Latest article detailed metrics
- Last 5 articles overview
- Global trends (30-day comparison)
- Significant insights (auto-detected)
- Top commenters with quality analysis
- Article performance comparison

---

## 🔍 Data Collection

### `devto_tracker.py`
Collect and store historical metrics from DEV.to API.

```bash
# Initialize database schema
python3 devto_tracker.py --api-key YOUR_KEY --init

# Collect full snapshot (articles, followers, metrics)
python3 devto_tracker.py --api-key YOUR_KEY --collect

# Collect daily analytics (read time, reaction breakdown)
python3 devto_tracker.py --api-key YOUR_KEY --collect-daily

# Collect referrers/traffic sources (UNDOCUMENTED ENDPOINT!)
python3 devto_tracker.py --api-key YOUR_KEY --collect-referrers

# Analyze growth trends
python3 devto_tracker.py --api-key YOUR_KEY --analyze-growth 30

# Analyze specific article velocity
python3 devto_tracker.py --api-key YOUR_KEY --analyze-article 3144468

# Custom database path
python3 devto_tracker.py --api-key YOUR_KEY --db custom.db --collect
```

---

## 📈 Quality Analytics

### `quality_analytics.py`
Analyze read time, reaction breakdown, and engagement quality.

```bash
# Full quality dashboard (default)
python3 quality_analytics.py
python3 quality_analytics.py --full

# Individual analyses
python3 quality_analytics.py --read-time        # Read time analysis
python3 quality_analytics.py --reactions        # Reaction breakdown
python3 quality_analytics.py --long-tail        # Long-tail performance
python3 quality_analytics.py --quality          # Quality scores

# Analyze specific article daily breakdown
python3 quality_analytics.py --article 3144468

# Custom database
python3 quality_analytics.py --db custom.db --full
```

**Metrics analyzed:**
- Average read time vs article length
- Completion rates
- Reaction types (like/unicorn/bookmark)
- Long-tail champions (old articles still getting views)
- Quality scores (completion + engagement)

---

## 🌐 Traffic Analytics

### `traffic_analytics.py`
Analyze referrers and traffic sources (uses undocumented `/api/analytics/referrers` endpoint).

```bash
# Full traffic dashboard (default)
python3 traffic_analytics.py
python3 traffic_analytics.py --full

# Individual analyses
python3 traffic_analytics.py --referrers        # Top traffic sources
python3 traffic_analytics.py --by-article       # Traffic per article
python3 traffic_analytics.py --seo              # SEO/Google performance
python3 traffic_analytics.py --social           # Social media performance

# Analyze specific article traffic sources
python3 traffic_analytics.py --article 3144468

# Custom database
python3 traffic_analytics.py --db custom.db --seo
```

**Traffic sources analyzed:**
- Direct / Bookmarks
- DEV.to internal
- Google (SEO)
- Twitter/X
- LinkedIn
- Reddit
- Hacker News
- Other external sites

---

## 🚀 Advanced Analytics

### `advanced_analytics.py`
Cross-analysis combining all historical data for deep insights.

```bash
# Full analytics report
python3 advanced_analytics.py --full-report

# Individual analyses
python3 advanced_analytics.py --follower-correlation    # Which articles brought followers
python3 advanced_analytics.py --evolution 3144468       # Detailed article evolution
python3 advanced_analytics.py --best-times              # Best publishing times
python3 advanced_analytics.py --comment-correlation     # Comments vs engagement

# Custom database
python3 advanced_analytics.py --db custom.db --full-report
```

**Advanced insights:**
- Article → Follower correlation (which articles brought followers)
- Engagement evolution over time (velocity, growth curves)
- Best publishing times (by day/hour)
- Comment engagement patterns

---

## 💬 Comment Analysis

### `comment_analyzer.py`
Deep dive into comment engagement and reader interaction.

```bash
# Full comment report
python3 comment_analyzer.py --full-report

# Individual analyses
python3 comment_analyzer.py --article 3144468      # Specific article comments
python3 comment_analyzer.py --compare              # Compare across articles
python3 comment_analyzer.py --engaged-readers      # Most engaged readers
python3 comment_analyzer.py --timing               # Comment timing patterns

# Custom database
python3 comment_analyzer.py --db custom.db --engaged-readers
```

**Comment metrics:**
- Total comments & unique commenters
- Timeline & velocity
- Top commenters
- Engagement depth (long vs short comments)
- Recent activity
- Comment timing distribution

---

## 🔧 Utility Scripts

### `quick_check.py`
Inspect database schema and sample data.

```bash
python3 quick_check.py
```

**Shows:**
- All tables in database
- Column schemas
- Sample data from each table

---

### `diagnose_reactions.py`
Compare reaction data between different data sources.

```bash
python3 diagnose_reactions.py
```

**Diagnoses:**
- Reaction counts from public API vs historical endpoint
- Data discrepancies
- Missing historical data

---

### `endpoint_hunter.py`
Discover hidden/undocumented DEV.to API endpoints.

```bash
python3 endpoint_hunter.py YOUR_API_KEY
```

**Tests:**
- Known documented endpoints
- Known undocumented endpoints
- Potential hidden endpoints
- Returns working endpoints with sample responses

---

## 🎯 Common Workflows

### Daily Collection Routine
```bash
# Collect all available data
python3 devto_tracker.py --api-key YOUR_KEY --collect
python3 devto_tracker.py --api-key YOUR_KEY --collect-daily
python3 devto_tracker.py --api-key YOUR_KEY --collect-referrers
```

### Quick Health Check
```bash
# See your current status
python3 dashboard.py
```

### Deep Article Analysis
```bash
# Analyze specific article from all angles
python3 quality_analytics.py --article 3144468
python3 traffic_analytics.py --article 3144468
python3 comment_analyzer.py --article 3144468
python3 advanced_analytics.py --evolution 3144468
```

### Performance Optimization
```bash
# Find what works best
python3 quality_analytics.py --quality          # Best quality articles
python3 traffic_analytics.py --seo              # SEO winners
python3 advanced_analytics.py --best-times      # Optimal posting times
python3 advanced_analytics.py --follower-correlation  # Follower magnets
```

### Reader Engagement Analysis
```bash
# Understand your audience
python3 comment_analyzer.py --engaged-readers   # Who are your fans?
python3 comment_analyzer.py --timing            # When do they engage?
python3 quality_analytics.py --reactions        # What do they react to?
```

---

## 📝 Notes

### API Key
All collection scripts require your DEV.to API key:
1. Go to https://dev.to/settings/extensions
2. Generate an API key
3. Use it with `--api-key YOUR_KEY`

### Database Location
- Default: `devto_metrics.db` in current directory
- Custom: Use `--db path/to/database.db` with any script

### Data Collection Frequency
- **Recommended:** Run collection daily for best trends
- **Minimum:** Weekly for meaningful analytics
- **Historical data:** `/api/analytics/historical` provides 90 days of daily metrics

### Undocumented Endpoints
⚠️ These endpoints are not in official API docs but work:
- `/api/analytics/historical` - Daily metrics with read time & reaction breakdown
- `/api/analytics/referrers` - Traffic sources (newly discovered!)

Use responsibly and be mindful of rate limits.

---

## 🆘 Troubleshooting

### "No data found"
- Run `python3 devto_tracker.py --api-key YOUR_KEY --init --collect` first
- Ensure you've published articles on DEV.to

### "API key error"
- Check your API key is valid
- Regenerate at https://dev.to/settings/extensions

### "Database locked"
- Close other scripts accessing the same database
- Only one write operation at a time

### Missing analytics
- Run `--collect-daily` and `--collect-referrers` for full data
- These use undocumented endpoints with richer metrics

---

## 📊 Quick Reference Table

| Script | Purpose | Key Commands |
|--------|---------|--------------|
| `dashboard.py` | Overview | `python3 dashboard.py` |
| `devto_tracker.py` | Collection | `--collect`, `--collect-daily`, `--collect-referrers` |
| `quality_analytics.py` | Quality | `--read-time`, `--reactions`, `--quality`, `--article ID` |
| `traffic_analytics.py` | Traffic | `--referrers`, `--seo`, `--social`, `--article ID` |
| `advanced_analytics.py` | Advanced | `--full-report`, `--evolution ID`, `--best-times` |
| `comment_analyzer.py` | Comments | `--engaged-readers`, `--timing`, `--article ID` |
| `quick_check.py` | Debug | `python3 quick_check.py` |
| `diagnose_reactions.py` | Debug | `python3 diagnose_reactions.py` |
| `endpoint_hunter.py` | Discovery | `python3 endpoint_hunter.py KEY` |

---

**Happy analyzing! 🚀**