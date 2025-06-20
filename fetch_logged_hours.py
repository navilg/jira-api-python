import os
from dotenv import load_dotenv
import requests
from datetime import datetime

# Load environment variables from .env
load_dotenv()

JIRA_AUTH_USERNAME = os.getenv("JIRA_AUTH_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")

def get_worklogs_in_date_range(username, start_date, end_date):
    """
    Fetches total hours logged by a user between two dates.
    Date format: "YYYY-MM-DD"
    """

    # Convert dates to Jira-compatible format (optional but useful for constraints)
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")

    # JQL query for issues where the user logged work in the date range
    jql_query = f'worklogAuthor = "{username}" AND worklogDate >= "{start_datetime}" AND worklogDate <= "{end_datetime}"'

    # Search for issues matching the criteria
    search_url = f"https://{JIRA_DOMAIN}/rest/api/2/search"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + JIRA_API_TOKEN
    }

    params = {
        "jql": jql_query,
        "fields": "key",  # Only fetching issue keys
        "maxResults": 1000  # Adjust if >1000 issues
    }

    issue_keys = []
    try:
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()  # Raises HTTPError for bad requests
        data = response.json()
        # print(data)
        issue_keys = [issue["key"] for issue in data["issues"]]
    except Exception as e:
        print(f"Error fetching issues: {e}")
        return 0.0

    # Fetch worklogs for each issue and aggregate logged time
    print(f"JIRA-KEY\tTime Logged (hrs)")
    total_hours = 0.0
    for issue_key in issue_keys:
        worklog_url = f"https://{JIRA_DOMAIN}/rest/api/2/issue/{issue_key}/worklog"
        try:
            response = requests.get(worklog_url, headers=headers)
            response.raise_for_status()
            worklogs = response.json().get("worklogs", [])
            for log in worklogs:
                log_date = log["started"].split("T")[0]  # Extract YYYY-MM-DD
                if log["author"]["name"] == username and start_datetime <= log_date <= end_datetime:
                    timeSpentHours = log["timeSpentSeconds"] / 3600 # Convert seconds to hours
                    total_hours += timeSpentHours
                    print(f"{issue_key}\t{timeSpentHours}")
        except Exception as e:
            print(f"Error fetching worklogs for {issue_key}: {e}")

    return round(total_hours, 2)

if __name__ == "__main__":
    username = os.getenv("JIRA_USERNAME")
    start_date = os.getenv("START_DATE")
    end_date = os.getenv("END_DATE")

    print(f"Logged-in User: {JIRA_AUTH_USERNAME}")
    print(f"Report generated for user: {username}")
    print(f"Worklog start date: {start_date}")
    print(f"Worklog end date: {end_date}")
    print("\n")
    total_hours = get_worklogs_in_date_range(username, start_date, end_date)
    print(f"\nTotal hours logged by {username} between {start_date} and {end_date}: {total_hours} hours\n")