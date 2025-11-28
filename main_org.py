import os
from github import Github, GithubException
import requests
from dotenv import load_dotenv

load_dotenv()

def get_github_client():
    """Get GitHub client, optionally with authentication token"""
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return Github(token)
    else:
        print("Warning: No GITHUB_TOKEN found. Using unauthenticated access (limited rate).")
        return Github()

def fetch_org_members(org_name: str):
    """
    Fetch all members from a GitHub organization
    
    Args:
        org_name: The GitHub organization name
        
    Returns:
        List of usernames
    """
    try:
        g = get_github_client()
        print(f"Fetching members from organization: {org_name}")
        
        org = g.get_organization(org_name)
        members = org.get_members()
        
        usernames = []
        count = 0
        for member in members:
            count += 1
            usernames.append(member.login)
            if count % 10 == 0:
                print(f"  Fetched {count} members so far...")
        
        print(f"✓ Loaded {len(usernames)} members from {org_name}")
        return usernames
        
    except GithubException as e:
        print(f"Error fetching organization members: {e}")
        if e.status == 404:
            print(f"Organization '{org_name}' not found or you don't have access to it.")
        elif e.status == 401:
            print("Authentication failed. Please check your GITHUB_TOKEN.")
        return []

def scan_v1_sha1_hulud(username: str):
    print(f"Scanning V1 SHA1 Hulud for user: {username}")
    try:
        g = get_github_client()
        user = g.get_user(username)
        # Check if username on github has a repo named Shai-Hulud
        try:
            user.get_repo("Shai-Hulud")
            return (True, f"https://github.com/{username}/Shai-Hulud")
        except GithubException:
            return (False, None)
    except GithubException as e:
        print(f"Error checking V1 for {username}: {e}")
        return (False, None)

def scan_v2_sha1_hulud(username: str):
    print(f"Scanning V2 SHA1 Hulud for user: {username}")
    try:
        g = get_github_client()
        user = g.get_user(username)
        # check if username on github has a repo containing "Sha1-Hulud: The Second Coming." in the description
        repos = user.get_repos()
        for repo in repos:
            if repo.description and "Sha1-Hulud: The Second Coming." in repo.description:
                return (True, repo.html_url)
        return (False, None)
    except GithubException as e:
        print(f"Error checking V2 for {username}: {e}")
        return (False, None)
    
def send_notification(message: str):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook_url:
        response = requests.post(webhook_url, json={"text": message})
        print(f"Notification sent with status code: {response.status_code}")
    else:
        print("Notification skipped: No SLACK_WEBHOOK_URL configured")

if __name__ == "__main__":
    # Get organization name from environment variable
    org_name = os.environ.get('GITHUB_ORG')
    
    if not org_name:
        print("Error: GITHUB_ORG environment variable not set.")
        print("Please add GITHUB_ORG=your-org-name to your .env file")
        exit(1)
    
    # Fetch users directly from organization
    users = fetch_org_members(org_name)
    
    if not users:
        print("No users found or unable to fetch organization members.")
        exit(1)
    
    print(f"\nStarting scan for {len(users)} users...\n")
    
    for user in users:
        v1, v1_url = scan_v1_sha1_hulud(user)
        v2, v2_url = scan_v2_sha1_hulud(user)
        if not v1 and not v2:
            print(f"User {user} is missing both V1 and V2 SHA1 Hulud repositories.")
            continue
        if v1:
            send_notification(f"User {user} has V1 SHA1 Hulud repository: {v1_url}")
        if v2:
            send_notification(f"User {user} has V2 SHA1 Hulud repository: {v2_url}")
