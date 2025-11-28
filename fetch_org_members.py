import csv
import os
from github import Github, GithubException
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

def fetch_org_members(org_name: str, output_file: str = 'users.csv'):
    """
    Fetch all members from a GitHub organization and save to CSV
    PyGithub automatically handles pagination, fetching all members across all pages.
    
    Args:
        org_name: The GitHub organization name
        output_file: Path to the output CSV file (default: users.csv)
    """
    try:
        g = get_github_client()
        print(f"Fetching members from organization: {org_name}")
        print("(PyGithub will automatically paginate through all results)")
        
        org = g.get_organization(org_name)
        members = org.get_members()
        
        usernames = []
        print("Collecting members...")
        count = 0
        for member in members:
            count += 1
            usernames.append(member.login)
            # Show progress every 10 members
            if count % 10 == 0:
                print(f"  Fetched {count} members so far...")
            else:
                print(f"  - {member.login}")
        
        # Write to CSV
        with open(output_file, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Username'])  # Header
            for username in usernames:
                writer.writerow([username])
        
        print(f"\n✓ Successfully saved {len(usernames)} members to {output_file}")
        return usernames
        
    except GithubException as e:
        print(f"Error fetching organization members: {e}")
        if e.status == 404:
            print(f"Organization '{org_name}' not found or you don't have access to it.")
        elif e.status == 401:
            print("Authentication failed. Please check your GITHUB_TOKEN.")
        return []

if __name__ == "__main__":
    # Replace 'your-org-name' with the actual organization name
    org_name = input("Enter the GitHub organization name: ").strip()
    
    if org_name:
        fetch_org_members(org_name)
    else:
        print("No organization name provided.")
