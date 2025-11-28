import csv
import os
from github import Github, GithubException
import requests
from dotenv import load_dotenv

load_dotenv()

def load_users_from_csv(file_path):
    users = []
    with open(file_path, mode='r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader:
            users.append(row[0])  # Assuming username is the first column
    return users

def get_github_client():
    """Get GitHub client, optionally with authentication token"""
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return Github(token)
    else:
        return Github()  # Unauthenticated (lower rate limit)

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
    response = requests.post(os.environ.get("SLACK_WEBHOOK_URL"), json={"text": message})
    print(f"Notification sent with status code: {response.status_code}")
if __name__ == "__main__":
    users = load_users_from_csv('users.csv')
    print("Loaded users:", users)
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
        