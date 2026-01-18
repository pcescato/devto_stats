# DEV.to Metrics Tracker 📊

**Automatic collection and historical analysis of your DEV.to metrics**

> "Without historical data, you only see snapshots. With historical data, you see trends."

## 🎯 Goals

1. **Automatically collect** all your DEV.to metrics
2. **Store historical snapshots** for long-term analysis
3. **Deep-dive into engagement** (comments, followers, etc.)
4. **Never lose data again** — the core idea behind the project

## 📦 Files

```
devto-metrics-tracker/
├── devto_tracker.py          # Main collection script
├── comment_analyzer.py       # Deep comment analysis
├── setup_automation.sh       # Automatic cron setup
├── advanced_analytics.py     # Advanced metrics analysis
├── anrety.py                 # Article analysis tool
├── checkcoverage.py          # Coverage verification
├── checkincremental.py       # Incremental data checks
├── cleanup_articles.py       # Cleanup of removed articles
├── cli_to_svg.py             # CLI-to-SVG converter
├── dashboard.py              # Metrics dashboard
├── diagnose.py               # Metrics diagnostics
├── fix.py                    # Error correction script
├── list_articles.py          # List collected articles
├── nlp_analyzer.py           # NLP analysis on comments
├── quality_analytics.py      # Article quality analysis
├── quick_check.py            # Quick metrics validation
├── traffic_analytics.py      # Traffic insights
```

## 🚀 Quick Install

### 1. Requirements

```bash
pip install requests python-dotenv
```

### 2. Configuration

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
DEVTO_API_KEY=your_actual_api_key_here
GEMINI_API_KEY=your_gemini_key_here  # Optional
```

Get your DEV.to API key from: https://dev.to/settings/extensions

### 3. Initialization

```bash
# Initialize database
python3 devto_tracker.py --init

# Collect your first snapshot
python3 devto_tracker.py --collect
```

**Note:** API keys are now loaded from `.env` file automatically. No need to pass them via command line!

### 3. Automation (recommended)

```bash
export DEVTO_API_KEY='your-api-key'
chmod +x setup_automation.sh
./setup_automation.sh
```

This will:

* Initialize the database
* Perform a test snapshot
* Create a cron wrapper
* Suggest different collection frequencies

## 📊 Database Structure

### Table: `snapshots`

Daily overview of all metrics.

| Column            | Description              |
| ----------------- | ------------------------ |
| `collected_at`    | Timestamp                |
| `total_articles`  | Total number of articles |
| `total_views`     | Total views              |
| `total_reactions` | Total reactions          |
| `total_comments`  | Total comments           |
| `follower_count`  | Total followers          |

### Table: `article_metrics`

Per-article metrics at each collection.

| Column         | Description |
| -------------- | ----------- |
| `collected_at` | Timestamp   |
| `article_id`   | Article ID  |
| `title`        | Title       |
| `views`        | Views       |
| `reactions`    | Reactions   |
| `comments`     | Comments    |
| `tags`         | JSON array  |

### Table: `follower_events`

| Column                     | Description |
| -------------------------- | ----------- |
| `collected_at`             | Timestamp   |
| `follower_count`           | Count       |
| `new_followers_since_last` | Increment   |

### Table: `comments`

| Column            | Description  |
| ----------------- | ------------ |
| `comment_id`      | Comment ID   |
| `article_id`      | Article      |
| `created_at`      | Timestamp    |
| `author_username` | Author       |
| `body_html`       | HTML content |
| `body_length`     | Length       |

## 🔍 Usage

### Manual collection

```bash
python3 devto_tracker.py --api-key YOUR_KEY --collect
python3 devto_tracker.py --api-key YOUR_KEY --analyze-growth 30
python3 devto_tracker.py --api-key YOUR_KEY --analyze-article 123456
```

### Comment analysis

```bash
python3 comment_analyzer.py --article 123456
python3 comment_analyzer.py --compare
python3 comment_analyzer.py --engaged-readers
python3 comment_analyzer.py --timing
python3 comment_analyzer.py --full-report
```

## 📈 Examples of Questions Answered

### Growth Analysis

* How many views did I gain per day this week?
* Which article has the best velocity (views/day)?
* When did I gain the most followers?

### Comment Deep-Dive

* Who are my most loyal readers?
* How fast do comments arrive after publication?
* Which articles spark the most conversation?
* What's the average comment length?

### Correlation Analysis

* Which article brought me the most followers?
* Is there a link between comment count and follower growth?
* Do long articles generate more engagement?

## ⏰ Recommended Collection Frequency

* **Early Stage (0–1000 followers):** 2×/day
* **Growth (1000–5000 followers):** 4×/day
* **Established (5000+ followers):** 6×/day

## 💡 Real-World Use Cases

### Case 1: Viral article

* Hour-by-hour growth curve
* Spike detection
* Correlating DEV.to staff comments
* Long-tail behavior

### Case 2: Follower growth

Daily follower increments and stabilization patterns.

### Case 3: Comment engagement

Deep qualitative and quantitative insights.

## 🔧 Maintenance

Backup, DB size checks, cleanup, VACUUM, and more.

## 📊 Useful SQL Queries

Includes:

* 7-day article growth
* Best days of the week
* Comment velocity

## 🚨 Troubleshooting

Database lock issues, rate-limit handling, missing data logs, etc.

## 🎯 Roadmap

* Web dashboard
* CSV export
* Email alerts
* Multi-API integration
* Sentiment analysis
* Performance prediction

## 📝 Important Notes

* DEV.to does **not** provide historical metrics
* Respect API limits
* Keep your DB private

## 🤝 Contributing

Fork → Branch → Commit → PR.

MIT License.

---

## 🧭 Inspiration & Related Tools

This project was inspired in part by the work of the DEV.to community, especially:

[devto-analytics-pro](https://github.com/GnomeMan4201/devto-analytics-pro) (by [GnomeMan4201](https://github.com/GnomeMan4201)) — a solid foundation for visualizing DEV.to metrics and understanding overall activity.

[devto-bot-audit](https://github.com/GnomeMan4201/devto-bot-audit) (by [GnomeMan4201](https://github.com/GnomeMan4201)) — a clever tool for identifying suspicious follower patterns and highlighting potential bot activity.

These tools helped shape the early direction of this tracker. However, this project goes further by focusing on historical data, automated collection, deep analytics, and a design closer to an ETL pipeline mixed with a lightweight CRM.

It aims to complement the existing ecosystem rather than replace it.

---

### 🚧 Status

**Still in progress. Check `TODO.md` for the roadmap toward the Community version.**
