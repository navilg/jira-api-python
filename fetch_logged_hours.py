import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import argparse
import pandas as pd

# Load environment variables from .env
load_dotenv()

JIRA_AUTH_USERNAME = os.getenv("JIRA_AUTH_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")

def get_worklogs_in_date_range(username, start_date, end_date, export_to_excel):
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
    total_hours = 0.0
    hour_logged_issue_key = {}
    hours_logged_date = {}
    for issue_key in issue_keys:
        worklog_url = f"https://{JIRA_DOMAIN}/rest/api/2/issue/{issue_key}/worklog"
        try:
            response = requests.get(worklog_url, headers=headers)
            response.raise_for_status()
            if issue_key not in hour_logged_issue_key:
                hour_logged_issue_key[issue_key] = 0
            worklogs = response.json().get("worklogs", [])
            for log in worklogs:
                log_date = log["started"].split("T")[0]  # Extract YYYY-MM-DD
                if log_date not in hours_logged_date:
                    hours_logged_date[log_date] = 0
                if log["author"]["name"] == username and start_datetime <= log_date <= end_datetime:
                    timeSpentHours = log["timeSpentSeconds"] / 3600 # Convert seconds to hours
                    total_hours += timeSpentHours
                    hour_logged_issue_key[issue_key] += timeSpentHours
                    hours_logged_date[log_date] += timeSpentHours
                
        except Exception as e:
            print(f"Error fetching worklogs for {issue_key}: {e}")
    print(f"JIRA_KEY\tHours_Logged")

    for jira_key in sorted(hour_logged_issue_key.keys()):
        if hour_logged_issue_key[jira_key] > 0:
            print(f"{jira_key}\t{hour_logged_issue_key[jira_key]}")

    print("\nDate\tHours_Logged")

    for log_date in sorted(hours_logged_date.keys()):
        if hours_logged_date[log_date] > 0:
            print(f"{log_date}\t{hours_logged_date[log_date]}")

    if export_to_excel:
        df = pd.DataFrame.from_dict(hour_logged_issue_key, orient='index', columns=['Hours logged'])
        df.index.name = 'Jira Issues'
        df.reset_index(inplace=True)
        df = df.sort_values(by=['Jira Issues'])

        df.to_excel(f'{username}_jira_hours_logged_{start_date}_{end_date}.xlsx', index=False, sheet_name='Worklog by issues')

        df = pd.DataFrame.from_dict(hours_logged_date, orient='index', columns=['Hours logged'])
        df.index.name = 'Date'
        df.reset_index(inplace=True)
        df = df.sort_values(by=['Date'])

        df.to_excel(f'{username}_jira_hours_logged_{start_date}_{end_date}.xlsx', index=False, sheet_name='Worklog by dates')

        with pd.ExcelWriter('jira_hours_logged.xlsx', engine='openpyxl') as writer:
            writer.book.properties.creator = "github.com/navilg"
            writer.book.properties.modifiedBy = "github.com/navilg"

    return round(total_hours, 2), jql_query

if __name__ == "__main__":

    flag_parser = argparse.ArgumentParser()
    flag_parser.add_argument("-u", "--username", required=True, help="Username for which you need to generate the report")
    flag_parser.add_argument("-s", "--startdate", required=True, help="Username for which you need to generate the report")
    flag_parser.add_argument("-e", "--enddate", required=True, help="Username for which you need to generate the report")
    flag_parser.add_argument("-x", "--export", action='store_true', default=False, help='If set, Data will be exported to excel sheet')

    args = flag_parser.parse_args()
    username = args.username
    start_date = args.startdate
    end_date = args.enddate
    export_to_excel = args.export

    # username = os.getenv("JIRA_USERNAME")
    # start_date = os.getenv("START_DATE")
    # end_date = os.getenv("END_DATE")

    if end_date == "today":
        end_date = datetime.today().strftime("%Y-%m-%d")

    print(f"Logged-in User: {JIRA_AUTH_USERNAME}")
    print(f"Report generated for user: {username}")
    print(f"Worklog start date: {start_date}")
    print(f"Worklog end date: {end_date}")
    print("\n")
    total_hours, jql_query = get_worklogs_in_date_range(username, start_date, end_date, export_to_excel)
    print(f"\nTotal hours logged: {total_hours} hours\n")
    print(f"To List above listed issues in jira, use below JQL query\n{jql_query}\n")