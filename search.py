import requests
import pandas as pd
import time

# Function to authenticate and get an access token
def get_access_token(client, secret):
    global ACCESS_TOKEN
    url = "https://api.snov.io/v1/oauth/access_token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client,
        "client_secret": secret
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        ACCESS_TOKEN = data['access_token']
        print("Access token obtained successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")

# Function to get all emails for a domain using Snov.io
def get_all_emails(domain):
    url = "https://api.snov.io/v2/domain-emails-with-info"
    params = {
        "domain": domain,
        "type": "all",
        "limit": 20,
        "access_token": ACCESS_TOKEN,
        "positions[]": ['CEO', 'CFO', 'CTO', 'COO', 'CMO', 'President', 'Vice President', 'Director', 'Manager', 'VP', 'Software Developer']
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'emails' in data:
            print(f"Emails found for domain {domain}: {len(data['emails'])}")
            return data['emails']
        else:
            print(f"No emails found for domain {domain}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error getting emails for domain {domain}: {e}")
        print(f"URL: {response.url}")
        return []

# Function to filter high-level employees
def filter_high_level_employees(emails):
    high_level_titles = ['CEO', 'CFO', 'CTO', 'COO', 'CMO', 'President', 'Vice President', 'Director']
    filtered_emails = [email for email in emails if any(title in email['position'] for title in high_level_titles)]
    return filtered_emails[:15]  # Limit to 10-15 high-level employees

# most imp function
def process_companies(companies_and_domains, client, secret):
    get_access_token(client, secret)
    all_emails = []
    for company, domain in companies_and_domains:
        if domain:
            emails = get_all_emails(domain)
            if emails:
                # high_level_emails = filter_high_level_employees(emails)
                for email in emails:
                    # if the first and last name are not already in the all_emails list
                    
                    
                        all_emails.append({
                            'company': company,
                            'domain': domain,
                            'email': email['email'],
                            'first name': email['firstName'],
                            'last name': email['lastName'],
                            'position': email['position']
                        })
                print(f"{len(emails)} emails found for domain {domain}")
            else:
                print(f"No emails found for domain {domain}")
        else:
            print(f"No domain found for company {company}")
    return all_emails

# reads company names from csv
def read_companies_from_csv(file_path):
    try:
        df = pd.read_csv(file_path, header=None)
        companies = df[0].tolist()
        return companies
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

# reads domains from csv
def read_domains_from_csv(file_path):
    try:
        df = pd.read_csv(file_path, header=None)
        domains = df[1].tolist()
        return domains
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []


# saves emails to csv
def save_emails_to_csv(emails, file_path):
    try:
        df = pd.DataFrame(emails)
        df.to_csv(file_path, index=False)
        print(f"Emails saved to {file_path}")
    except Exception as e:
        print(f"Error saving to CSV file: {e}")

def run_email_extraction(input_csv_file_path, output_csv_file_path, client_id, client_secret):
    companies = read_companies_from_csv(input_csv_file_path)
    domains = read_domains_from_csv(input_csv_file_path)
    companies_and_domains = list(zip(companies, domains))
    if companies:
        emails = process_companies(companies_and_domains, client_id, client_secret)
        if emails:
            save_emails_to_csv(emails, output_csv_file_path)
            return output_csv_file_path, len(emails)
        else:
            print("No emails found.")
            return None, 0
    else:
        print("No companies to process.")
        return None, 0

# # paths to input CSV file and output CSV file
# input_csv_file_path = 'companies.csv'
# output_csv_file_path = 'emails.csv'

# # read companies from CSV and process them
# run_email_extraction(input_csv_file_path, output_csv_file_path)