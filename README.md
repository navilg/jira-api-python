# Jira APIs

## Requirements

1. Python >= 3.11
2. Windows powershell or Linux shell terminal
3. Jira URL

## How to use it ?

### Generate Personal Access Token

1. Login to Jira with your account

2. Click on your Avatar from top right corner --> Click on profile

3. Click on Personal Access Tokens

4. Create Token

5. COpy the token and keep it safe and secure

### Install modules and dependencies

```bash
# To create and activate virtual environment
# virtualenv .venv
# source .venv/bin/activate
# .venv\Scripts\activate.ps1 # For windows powershell

# Install modules and dependencies
pip install -r requirements.txt
```

### Run the python script

1. Update `.env` file with your credential and details

```bash
cp .env.example .env
 # Update .env file
 ```

2. Run the script

```bash
python fetch_logged_hours.py
```

