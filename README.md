# GitHub Sha1-Hulud Detector

A Python tool to detect and monitor GitHub repositories related to the Sha1-Hulud project across organization members.

## Features

- **Fetch Organization Members**: Automatically retrieve all members from a GitHub organization and save them to CSV
- **V1 Detection**: Scan for repositories named `   `
- **V2 Detection**: Scan for repositories with "Sha1-Hulud: The Second Coming." in their description
- **Slack Notifications**: Send alerts when repositories are detected
- **Automated Pagination**: Handles large organizations with automatic API pagination

## Prerequisites

- Python 3.7+
- GitHub Personal Access Token (recommended for higher rate limits)
- Slack Webhook URL (optional, for notifications)

## Installation

1. Clone the repository:
```bash
git clone git@github.com:Joeri-Abbo/Github-Sha1-Hulud-detector.git
cd Github-Sha1-Hulud-detector
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

pip install -r requirments.txt
```

3. Set up your environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your tokens:
```
GITHUB_TOKEN=your_github_token_here
GITHUB_ORG=your_organization_name
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
```

## Getting Your GitHub Token

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `public_repo` - for reading public repositories
   - `read:org` - for reading organization member information
4. Copy the token and add it to your `.env` file

## Usage

### Fetch Organization Members

Run this script to populate `users.csv` with all members from a GitHub organization:

```bash
python fetch_org_members.py
```

You'll be prompted to enter the organization name. The script will:
- Fetch all members (automatically paginated)
- Display progress as it collects members
- Save all usernames to `users.csv`

### Scan for Sha1-Hulud Repositories

Once you have `users.csv` populated, run the main scanner:

```bash
python main.py
```

This will:
- Load all users from `users.csv`
- Check each user for:
  - **V1**: A repository named `Shai-Hulud`
  - **V2**: Any repository with "Sha1-Hulud: The Second Coming." in its description
- Send Slack notifications when repositories are found (if webhook configured)

### Scan Organization Directly (Alternative)

Instead of using a CSV file, you can scan an organization directly using `main_org.py`:

```bash
python main_org.py
```

This will:
- Fetch all members from the organization specified in `GITHUB_ORG` (from `.env`)
- Scan each member for Sha1-Hulud repositories in real-time
- Send Slack notifications when repositories are found

**Note**: This requires the `GITHUB_ORG` environment variable to be set in your `.env` file.

### Using the Run Script

For convenience, use the provided run script:

```bash
sh run.sh
```

## API Rate Limits

GitHub API rate limits:
- **Without authentication**: 60 requests/hour
- **With authentication**: 5,000 requests/hour

**Recommendation**: Always use a GitHub token to avoid hitting rate limits, especially when scanning many users.

## File Structure

```
.
├── fetch_org_members.py  # Fetch organization members to CSV
├── main.py               # Main scanner (reads from users.csv)
├── main_org.py          # Alternative scanner (fetches org members directly)
├── users.csv            # List of usernames to scan
├── requirments.txt      # Python dependencies
├── run.sh              # Convenience script
├── .env.example        # Example environment variables
└── README.md           # This file
```

## Configuration

### Environment Variables

- `GITHUB_TOKEN` - GitHub Personal Access Token (required for org access)
- `GITHUB_ORG` - GitHub organization name (required for `main_org.py`)
- `SLACK_WEBHOOK_URL` - Slack webhook for notifications (optional)

### CSV Format

The `users.csv` file should have the following format:

```csv
Username
user1
user2
user3
```

## Examples

### Fetch Homebrew Organization Members
```bash
$ python fetch_org_members.py
Enter the GitHub organization name: Homebrew
Fetching members from organization: Homebrew
(PyGithub will automatically paginate through all results)
Collecting members...
  - member1
  - member2
  Fetched 10 members so far...
  ...
✓ Successfully saved 150 members to users.csv
```

### Scan Users for Repositories
```bash
$ python main.py
Loaded users: ['user1', 'user2', 'user3']
Scanning V1 SHA1 Hulud for user: user1
Scanning V2 SHA1 Hulud for user: user1
User user1 has V1 SHA1 Hulud repository: https://github.com/user1/Shai-Hulud
Notification sent with status code: 200
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Joeri Abbo