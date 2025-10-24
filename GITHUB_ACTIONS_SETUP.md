# GitHub Actions Setup

This guide explains how to set up automated PNR status checking using GitHub Actions.

## Overview

The GitHub Actions workflow (`.github/workflows/check-pnr-status.yml`) will:
- Run automatically every hour
- Check all PNR numbers configured in `PNR_LIST`
- Send Google Chat notifications if status changes
- Commit the updated `pnr_status_history.json` back to the repository

## Setup Instructions

### Step 1: Push Code to GitHub

1. Create a new repository on GitHub
2. Push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

### Step 2: Configure GitHub Secret

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secret:
   - **Name:** `GOOGLE_CHAT_WEBHOOK`
   - **Value:** Your Google Chat webhook URL (from SETUP_NOTIFICATIONS.md)
5. Click **Add secret**

### Step 3: Update .gitignore

The `.gitignore` file already excludes `pnr_status_history.json` from local commits. However, since we want the GitHub Actions workflow to commit this file, we need to force-add it once:

```bash
# Remove pnr_status_history.json from .gitignore temporarily for GitHub Actions
# OR force add it once:
git add -f pnr_status_history.json
git commit -m "Add PNR status history for GitHub Actions tracking"
git push
```

Then add it back to `.gitignore` to exclude it from local development.

### Step 4: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. GitHub Actions should be enabled by default
4. You should see the "Check PNR Status" workflow listed

### Step 5: Test the Workflow

You can manually trigger the workflow to test it:

1. Go to **Actions** tab
2. Click on "Check PNR Status" workflow
3. Click **Run workflow** → **Run workflow**
4. Wait for the workflow to complete
5. Check the workflow logs for any errors
6. Verify that `pnr_status_history.json` was updated in the repository

## Workflow Schedule

The workflow runs on this schedule:
- **Cron:** `0 * * * *` (every hour at minute 0)
- **Time zone:** UTC

To change the schedule, edit `.github/workflows/check-pnr-status.yml`:

```yaml
on:
  schedule:
    - cron: '0 * * * *'  # Every hour
    # - cron: '*/30 * * * *'  # Every 30 minutes
    # - cron: '0 */2 * * *'  # Every 2 hours
    # - cron: '0 9 * * *'  # Daily at 9 AM UTC
```

**Cron syntax:** `minute hour day month weekday`

Examples:
- `0 * * * *` - Every hour
- `*/30 * * * *` - Every 30 minutes
- `0 */2 * * *` - Every 2 hours
- `0 6,12,18 * * *` - At 6 AM, 12 PM, and 6 PM UTC
- `0 9 * * *` - Daily at 9 AM UTC

## Monitoring

### View Workflow Runs

1. Go to **Actions** tab in your repository
2. Click on "Check PNR Status" workflow
3. View recent runs and their status

### Check Logs

1. Click on any workflow run
2. Click on the "check-status" job
3. Expand each step to see detailed logs

### View Commit History

All automated updates will be committed with messages like:
```
Update PNR status - 2025-10-24 14:30:00 UTC
```

You can view these commits in the repository's commit history.

## Notifications

When status changes are detected:
1. The script logs the change to console (visible in workflow logs)
2. A Google Chat notification is sent (if webhook is configured)
3. The updated status is committed to the repository

## Troubleshooting

### Workflow not running

- Check if GitHub Actions is enabled in your repository settings
- Verify the cron schedule is correct
- GitHub may delay scheduled workflows during high load

### Authentication errors when pushing

- Ensure the workflow has `permissions: contents: write`
- Check if branch protection rules are blocking the push

### Google Chat notifications not working

- Verify `GOOGLE_CHAT_WEBHOOK` secret is set correctly
- Check workflow logs for error messages
- Test the webhook URL manually

### No changes committed

This is normal if:
- PNR status hasn't changed since last check
- The workflow uses `git diff --staged --quiet` to only commit if changes exist

## Security Notes

- Never commit your `GOOGLE_CHAT_WEBHOOK` URL directly to code
- Always use GitHub Secrets for sensitive values
- The webhook URL is only accessible to workflow runs
- GitHub Actions logs may contain API responses, review before sharing

## Cost Considerations

- GitHub Actions is free for public repositories
- Private repositories have usage limits (2,000 minutes/month on free plan)
- This workflow uses minimal compute time (~1-2 minutes per run)
- Running hourly = ~720 minutes/month (well within free tier)
