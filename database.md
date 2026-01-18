================================================================================
DATABASE SCHEMA
================================================================================

Tables found: 12
  • snapshots
  • sqlite_sequence
  • article_metrics
  • follower_events
  • comments
  • followers
  • daily_analytics
  • referrers
  • article_content
  • article_code_blocks
  • article_links
  • comment_insights

================================================================================
ARTICLE_METRICS TABLE SCHEMA
================================================================================

Columns in article_metrics:
  id                             INTEGER
  collected_at                   TIMESTAMP       NOT NULL
  article_id                     INTEGER         NOT NULL
  title                          TEXT
  slug                           TEXT
  published_at                   TIMESTAMP
  views                          INTEGER
  reactions                      INTEGER
  comments                       INTEGER
  reading_time_minutes           INTEGER
  tags                           TEXT
  is_deleted                     INTEGER

================================================================================
SAMPLE DATA FROM ARTICLE_METRICS
================================================================================

Latest record:
  id                             = 1569
  collected_at                   = 2026-01-18T11:00:01.472919+00:00
  article_id                     = 2783785
  title                          = I Replaced My $6/Month VPS with a 2017 Laptop and Cut Cos...
  slug                           = how-i-replaced-my-6month-vps-with-a-2017-laptop-and-why-i...
  published_at                   = 2025-08-19T19:56:30.101Z
  views                          = 75
  reactions                      = 0
  comments                       = 0
  reading_time_minutes           = 1
  tags                           = ["docker", "selfhosted", "homelab"]
  is_deleted                     = 0

================================================================================
DAILY_ANALYTICS TABLE SCHEMA
================================================================================

Columns in daily_analytics:
  id                             INTEGER
  article_id                     INTEGER         NOT NULL
  date                           DATE            NOT NULL
  page_views                     INTEGER
  average_read_time_seconds      INTEGER
  total_read_time_seconds        INTEGER
  reactions_total                INTEGER
  reactions_like                 INTEGER
  reactions_readinglist          INTEGER
  reactions_unicorn              INTEGER
  comments_total                 INTEGER
  follows_total                  INTEGER
  collected_at                   TIMESTAMP       NOT NULL
