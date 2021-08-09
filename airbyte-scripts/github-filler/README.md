# Create Template GitHub Repository

## Prerequiereties
### 1. Create a repository on www.github.com
### 2. Create an api key https://github.com/settings/tokens (select all checkboxes)

---

### 1. In root folder create python virtualenv
    python -m venv .env
### 2. Activate python virtualenv
    source .env/bin/activate
### 3. Install libraries
    pip install requirements.txt
### 4. Then just run and enter credentials
    ./run.sh

---

## After all the steps, you will have a GitHub repository with data that covers almost all GitHub streams (in Airbyte connectors), but you will need to add some data manually.
    1. Collaborators (invite collaborators)
    2. Asignees (asignee issues to collaborators)
    3. Teams (create a teams inside organization)
## All of this data can be generated through the GitHub site.
