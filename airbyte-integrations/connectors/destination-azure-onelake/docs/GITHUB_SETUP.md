# GitHub Repository Setup — OneLake Airbyte Destination Connector

Use these steps to create a public (or private) GitHub repo named **OneLake Airbyte Destination Connector** and push this connector to your account.

---

## Option A: New repo with only this connector (recommended)

This gives you a standalone repo that others can browse and clone. Building from source still requires the [Airbyte monorepo](https://github.com/airbytehq/airbyte); the README in the repo explains that.

### 1. Create the repository on GitHub

- Go to [github.com/new](https://github.com/new).
- **Repository name:** `OneLake-Airbyte-Destination-Connector` (or `onelake-airbyte-destination-connector`).
- **Description:** `Airbyte destination connector for Microsoft Fabric OneLake (Lakehouse Files). Supports Service Principal and Managed Identity.`
- Choose **Public** (or Private).
- Do **not** initialize with a README, .gitignore, or license (you already have them in the connector).
- Click **Create repository**.

### 2. Push the connector from your machine

From your **Airbyte monorepo root** (e.g. `~/airbyte-dev`), run:

```bash
# Add your new GitHub repo as a remote (replace YOUR_USERNAME with your GitHub username)
git remote add onelake-connector https://github.com/YOUR_USERNAME/OneLake-Airbyte-Destination-Connector.git

# Create a branch that contains only the connector directory
git subtree split -P airbyte-integrations/connectors/destination-azure-onelake -b onelake-connector

# Push that branch to the new repo as main
git push onelake-connector onelake-connector:main
```

If you prefer to push from **inside** the connector directory (no subtree):

```bash
cd airbyte-integrations/connectors/destination-azure-onelake

# Create a new repo (requires GitHub CLI: gh repo create)
gh repo create OneLake-Airbyte-Destination-Connector --public --source=. --remote=origin --push --description "Airbyte destination connector for Microsoft Fabric OneLake"
```

If you don’t use `gh`, instead:

1. Create the empty repo on GitHub (step 1 above).
2. In the connector directory, init a new git repo and push:
   ```bash
   cd airbyte-integrations/connectors/destination-azure-onelake
   git init
   git add .
   git commit -m "Initial commit: OneLake Airbyte destination connector"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/OneLake-Airbyte-Destination-Connector.git
   git push -u origin main
   ```

### 3. Add repo description and topics

On the GitHub repo page:

- **About** → set description and **Topics**, e.g.: `airbyte`, `microsoft-fabric`, `onelake`, `data-connector`, `elt`, `data-engineering`.

---

## Option B: Fork Airbyte and use your fork

If you want the connector to live inside the full Airbyte codebase:

1. Fork [airbytehq/airbyte](https://github.com/airbytehq/airbyte) to your account.
2. Push your branch (with the OneLake connector) to your fork.
3. In the fork’s **About** or README, point to `airbyte-integrations/connectors/destination-azure-onelake` as the OneLake destination connector.

Building and tagging the image then happens from your fork as in [BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md).

---

## After the repo is created

- Add a **LICENSE** file (e.g. MIT) if you want.
- Use **Issues** and **Discussions** for community feedback.
- In the main README, keep the link to [Build, deploy & operations](BUILD_AND_DEPLOY.md) so users know how to build the Docker image (with the Airbyte monorepo) and deploy.
