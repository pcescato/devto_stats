# 🛠️ Roadmap & Upcoming Features

This project is a **Work In Progress**. While the core ETL pipeline and sentiment analysis are functional, the following features are planned for the upcoming "Community" version:

## 📈 Analytics & Engine
- [ ] **Topic Modeling**: Integration of a layer to extract recurring technical themes from comments.
- [ ] **Markdown Reporting**: Automatic generation of `DAILY_REPORT.md` for a quick morning brief.
- [ ] **Velocity Tracking**: Refactoring `sismograph.py` into the main automated workflow.

## 👥 Community & Engagement
- [ ] **Author Trust Score**: Implementation of a reputation system to identify and highlight loyal technical readers.
- [ ] **Unanswered Question Refinement**: Advanced filtering to further separate real technical queries from sophisticated spam.
- [ ] **Engagement Trends**: Moving beyond snapshots to see how community sentiment evolves per article over months.

## 🛠️ Maintenance
- [ ] Better documentation of the duality between *Velocity* (sismograph) and *Intelligence* (analyzer).
- [ ] Exporting insights to JSON for external dashboard integration.

## 📝 Content Versioning (Urgent)
- [ ] **Create `article_history` table**: Store `title`, `body_markdown`, and `tags` indexed by `article_id` and `version_timestamp`.
- [ ] **Detection Logic**: Update the fetcher to compare incoming content with the latest stored version. Trigger a new entry if a delta is detected.
- [ ] **Impact Analysis**: Correlate content updates with velocity spikes in `sismograph.py` (Did the title change boost views?).