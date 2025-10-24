# PNR Status Notifier

Automated Indian Railway PNR status checker with Google Chat notifications.

## Features

- 🔍 Check multiple PNR statuses automatically
- 🔔 Get instant Google Chat notifications when status changes
- 📊 Track status history over time
- ⚡ Automatic retry logic for API reliability
- 🤖 GitHub Actions integration for hourly automated checks
- 🛡️ Comprehensive error handling

## Quick Start

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager
- Google Chat webhook (optional, for notifications)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pnr-notify-update.git
   cd pnr-notify-update
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Configure PNR numbers in `get_status.py`:
   ```python
   PNR_LIST = [
       "8439632790",
       "8239524689",
       # Add your PNR numbers here
   ]
   ```

4. Run the script:
   ```bash
   uv run python get_status.py
   ```

## Configuration

### Google Chat Notifications

Set up notifications to get alerted when PNR status changes:

```bash
export GOOGLE_CHAT_WEBHOOK="https://chat.googleapis.com/v1/spaces/YOUR_WEBHOOK_URL"
```

See [SETUP_NOTIFICATIONS.md](SETUP_NOTIFICATIONS.md) for detailed instructions.

### GitHub Actions (Automated Checks)

Run checks automatically every hour using GitHub Actions:

1. Push code to GitHub
2. Add `GOOGLE_CHAT_WEBHOOK` as a repository secret
3. Enable GitHub Actions

See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for detailed instructions.

## Usage

### Check Status Manually

```bash
uv run python get_status.py
```

Output:
```
Checking 2 PNR(s)...

Checking PNR: 8439632790
  Attempt 1/5... Success!
  Status updated at 2025-10-24T14:36:41.236923
  Current Status: GNWL  21
  Prediction: Low Chance (3%)
  No change in status
```

### Status History

Status for each PNR is stored in `pnr_status_history.json`:

```json
{
  "8439632790": {
    "timestamp": "2025-10-24T14:36:41.236923",
    "train": "22230 CSMT VANDEBHARAT",
    "doj": "27-10-2025",
    "route": "Khed → Mumbai",
    "departure": "18:57",
    "passenger_status": [
      {
        "number": 1,
        "booking_status": "GNWL  44",
        "current_status": "GNWL  21",
        "prediction": "Low Chance",
        "prediction_percentage": "3"
      }
    ]
  }
}
```

## Architecture

- **Single-file application**: All logic in `get_status.py`
- **Change detection**: Compares previous vs current status
- **Retry logic**: Up to 5 attempts per PNR (API sometimes fails on first try)
- **Error handling**: Network errors, timeouts, JSON parsing, file I/O
- **Notification system**: Google Chat webhooks for real-time alerts

## Documentation

- [SETUP_NOTIFICATIONS.md](SETUP_NOTIFICATIONS.md) - Configure Google Chat notifications
- [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) - Set up automated checking
- [CLAUDE.md](CLAUDE.md) - Development guidelines for AI assistants

## API

Uses the ConfirmTkt API:
```
POST https://cttrainsapi.confirmtkt.com/api/v2/ctpro/mweb/{PNR}
```

**Note**: The API requires specific headers and may return "Invalid PNR" on first attempts. The retry logic handles this automatically.

## Contributing

This is a personal project for tracking PNR statuses. Feel free to fork and modify for your needs.

## Security

- Never commit webhook URLs or API keys to code
- Use environment variables for sensitive values
- Review GitHub Actions logs before sharing publicly
- PNR numbers and status data may be sensitive - configure `.gitignore` accordingly

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool uses the ConfirmTkt API which is a third-party service. The accuracy of predictions and status information depends on the API's data quality. Use at your own discretion.
