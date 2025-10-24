# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python script that queries the ConfirmTkt API to check Indian railway PNR (Passenger Name Record) status and tracks changes over time in a JSON file.

## Development Commands

- Run the script: `uv run python get_status.py`
- Install dependencies: `uv pip install requests`
- List installed packages: `uv pip list`
- Setup notifications: See `SETUP_NOTIFICATIONS.md`

## Environment Variables

- `GOOGLE_CHAT_WEBHOOK`: Google Chat webhook URL for status change notifications
  - See `.env.example` for format
  - Optional: Script works without it but won't send notifications

## Architecture

Single-file application (`get_status.py`) that:
- Supports checking multiple PNR numbers (configured in `PNR_LIST`)
- Makes POST requests to the ConfirmTkt API for each PNR
- Implements retry logic (up to 5 attempts) as the API sometimes returns "Invalid PNR" on first calls
- Handles network errors, timeouts, JSON parsing errors, and file I/O issues
- Tracks latest status per PNR in `pnr_status_history.json` (PNR number as key)
- Detects status changes by comparing with previous checks
- Sends Google Chat notifications when status changes (requires webhook configuration)
- Extracts key information: current waitlist position, booking status, confirmation prediction

## Error Handling

The script includes comprehensive exception handling:
- Network/connection errors with automatic retry
- HTTP errors (4xx, 5xx responses)
- JSON parsing errors
- File I/O errors for history file
- Missing or malformed data in API responses
- 10-second timeout on API requests

## Dependencies

Uses only the `requests` library for HTTP calls. Managed via `uv` for Python environment management.
