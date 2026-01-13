#!/bin/bash
# 
# Setup script for automated DEV.to metrics collection
# This configures a cron job to collect metrics regularly
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRACKER_SCRIPT="$SCRIPT_DIR/devto_tracker.py"
DB_PATH="$SCRIPT_DIR/devto_metrics.db"
LOG_DIR="$SCRIPT_DIR/logs"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔧 DEV.to Tracker - Automated Collection Setup"
echo "================================================"
echo ""

# Check if API key is provided
if [ -z "$DEVTO_API_KEY" ]; then
    echo "❌ Error: DEVTO_API_KEY environment variable not set"
    echo ""
    echo "Usage:"
    echo "  export DEVTO_API_KEY='your-api-key'"
    echo "  ./setup_automation.sh"
    exit 1
fi

# Create logs directory
mkdir -p "$LOG_DIR"
echo "✅ Logs directory: $LOG_DIR"

# Initialize database
echo "📦 Initializing database..."
python3 "$TRACKER_SCRIPT" --api-key "$DEVTO_API_KEY" --db "$DB_PATH" --init
echo "✅ Database initialized: $DB_PATH"

# Test collection
echo ""
echo "🧪 Running test collection..."
python3 "$TRACKER_SCRIPT" --api-key "$DEVTO_API_KEY" --db "$DB_PATH" --collect
echo "✅ Test collection successful"

# Create wrapper script for cron
CRON_WRAPPER="$SCRIPT_DIR/collect_metrics.sh"
cat > "$CRON_WRAPPER" << EOF
#!/bin/bash
# Auto-generated wrapper for cron
export DEVTO_API_KEY='$DEVTO_API_KEY'
cd "$SCRIPT_DIR"
python3 "$TRACKER_SCRIPT" --api-key "\$DEVTO_API_KEY" --db "$DB_PATH" --collect >> "$LOG_DIR/collection.log" 2>&1
EOF

chmod +x "$CRON_WRAPPER"
echo "✅ Cron wrapper created: $CRON_WRAPPER"

echo ""
echo "📋 RECOMMENDED CRON SCHEDULES"
echo "================================================"
echo ""
echo "Option 1: Every 6 hours (4x per day)"
echo -e "${GREEN}0 */6 * * * $CRON_WRAPPER${NC}"
echo ""
echo "Option 2: Every 12 hours (2x per day)"
echo -e "${GREEN}0 */12 * * * $CRON_WRAPPER${NC}"
echo ""
echo "Option 3: Daily at 2 AM"
echo -e "${GREEN}0 2 * * * $CRON_WRAPPER${NC}"
echo ""
echo "Option 4: Twice daily (6 AM and 6 PM)"
echo -e "${GREEN}0 6,18 * * * $CRON_WRAPPER${NC}"
echo ""

echo "📝 To add to crontab:"
echo "  1. Edit crontab: ${YELLOW}crontab -e${NC}"
echo "  2. Add one of the lines above"
echo "  3. Save and exit"
echo ""

echo "🔍 To view collection logs:"
echo "  ${YELLOW}tail -f $LOG_DIR/collection.log${NC}"
echo ""

echo "✅ Setup complete!"
