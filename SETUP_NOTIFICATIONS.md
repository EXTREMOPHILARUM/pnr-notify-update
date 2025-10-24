# Setting Up Google Chat Notifications

This guide will help you set up Google Chat notifications for PNR status changes.

## Step 1: Create a Google Chat Space (if needed)

1. Go to [Google Chat](https://chat.google.com)
2. Create a new space or use an existing one where you want to receive notifications
3. Name it something like "PNR Status Alerts"

## Step 2: Create a Webhook

1. In your Google Chat space, click on the space name at the top
2. Select **Apps & integrations**
3. Click **Add webhooks**
4. Give your webhook a name (e.g., "PNR Status Monitor")
5. Optionally add an avatar URL
6. Click **Save**
7. Copy the webhook URL (it will look like: `https://chat.googleapis.com/v1/spaces/...`)

## Step 3: Configure the Webhook URL

Set the webhook URL as an environment variable (recommended for security):

### Option A: Temporary (current session only)
```bash
export GOOGLE_CHAT_WEBHOOK="https://chat.googleapis.com/v1/spaces/YOUR_WEBHOOK_URL"
```

### Option B: Permanent (recommended)

**For macOS/Linux (bash):**
1. Edit your `~/.bashrc` or `~/.bash_profile`:
   ```bash
   echo 'export GOOGLE_CHAT_WEBHOOK="https://chat.googleapis.com/v1/spaces/YOUR_WEBHOOK_URL"' >> ~/.bashrc
   ```
2. Reload the file:
   ```bash
   source ~/.bashrc
   ```

**For macOS/Linux (zsh):**
1. Edit your `~/.zshrc`:
   ```bash
   echo 'export GOOGLE_CHAT_WEBHOOK="https://chat.googleapis.com/v1/spaces/YOUR_WEBHOOK_URL"' >> ~/.zshrc
   ```
2. Reload the file:
   ```bash
   source ~/.zshrc
   ```

**For Windows:**
1. Open System Properties > Environment Variables
2. Create a new User variable:
   - Name: `GOOGLE_CHAT_WEBHOOK`
   - Value: Your webhook URL

### Verify the environment variable is set:
```bash
echo $GOOGLE_CHAT_WEBHOOK
```

## Step 4: Test the Notification

To test if notifications work:

1. Run the script once to establish the baseline status:
   ```bash
   uv run python get_status.py
   ```

2. Manually change a status in `pnr_status_history.json` to simulate a change:
   - Open `pnr_status_history.json`
   - Change a `current_status` value (e.g., from "GNWL  21" to "GNWL  20")
   - Save the file

3. Run the script again:
   ```bash
   uv run python get_status.py
   ```

4. You should see "🔔 Status has changed!" in the output and receive a notification in Google Chat

## Step 5: Set Up Automated Checking

To automatically check for status changes every hour, you can use cron (macOS/Linux) or Task Scheduler (Windows).

### Using cron (macOS/Linux):

1. Open your crontab:
   ```bash
   crontab -e
   ```

2. Add this line to check every hour:
   ```
   0 * * * * cd /Users/extremo/ppr/pnr-notify-update && /path/to/uv run python get_status.py >> /tmp/pnr_check.log 2>&1
   ```

3. Adjust the schedule as needed:
   - Every 30 minutes: `*/30 * * * *`
   - Every 2 hours: `0 */2 * * *`
   - Every day at 9 AM: `0 9 * * *`

## Notification Format

When a status changes, you'll receive a Google Chat message with:
- 🚂 Icon to indicate train notification
- PNR number
- Train name and number
- Journey date
- Route
- Previous status → New status
- Confirmation prediction
- Timestamp of the update

## Troubleshooting

### No notifications received

1. Verify the webhook URL is correct in `get_status.py`
2. Check that the webhook hasn't been deleted in Google Chat
3. Look for error messages when running the script
4. Ensure you have internet connectivity

### Notifications not being triggered

1. Verify that the status has actually changed
2. Check `pnr_status_history.json` to see the stored statuses
3. The script only sends notifications when `current_status` changes

### Multiple notifications

- Each time the script runs and detects a change, it will send a notification
- Make sure you're not running the script too frequently
