# On GCP (Compute Engine)

:information_source: The instructions have been tested on `Debian GNU/Linux 10 (buster)`

## Initial Setup

:information_source: These steps only need to be done once (no matter how many people use the Compute Engine instance)


### Set up a Google Cloud Service account
1. Create a service account (if you do not already have one)
   1. Follow the instructions on either the `Console` or `gcloud` tab: https://cloud.google.com/iam/docs/creating-managing-service-accounts
   1. Assign these roles to the service account
      1. Roles to assign
         1. `roles/cloudsql.viewer`
         1. `roles/cloudsql.client`
         1. `roles/cloudsql.instanceUser`
         1. If you will be connecting to BigQuery as a source or destination
            1. `roles/bigquery.user`
            1. `roles/bigquery.dataEditor`


### Create a new instance
1. Launch a new instance 
   * ![](../.gitbook/assets/gcp_ce_launch.png)
   1. Go to https://console.cloud.google.com/compute/instances
   1. Click `CREATE INSTANCE`
      1. Configure new instance 
         * ![](../.gitbook/assets/gcp_ce_configure.png)
         1. Machine Configuration
            1. For testing out Airbyte, an `e2.medium` instance is likely sufficient. Airbyte uses a lot of disk space with images and logs, so make sure to provision at least 30GBs of disk per node. 
            1. For long-running Airbyte installations, we recommend a `n1-standard-2` instance.
         1. Identity and API access
            1. Service Account: `{{SERVICE_ACCOUNT_NAME}}`
            1. Access scopes: `Allow default access`
         1. Click `Create`


### Install environment

:information_source: The following commands will be entered either on your local terminal or in your ssh session on the instance terminal. The comments above each command block will indicate where to enter the commands.

1. Set variables in your terminal
   ```bash
   # In your workstation terminal
   PROJECT_ID={{PROJECT_NAME}}
   INSTANCE_NAME={{COMPUTE_ENGINE_INSTANCE_NAME}}
   ```
1. `gcloud`
   1. Install gcloud
      1. MacOS: 
         ```bash
         # In your workstation terminal
         brew install --cask google-cloud-sdk
         gcloud init # Follow instructions
         ```
      1. Ubuntu/Linux/Windows WSL
         ```bash
         # In your workstation terminal
         echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
         sudo apt-get install apt-transport-https ca-certificates gnupg
         curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
         sudo apt-get update && sudo apt-get install google-cloud-sdk
         ```
    1. Verify you can see your instance in the results of
      ```bash
      # In your workstation terminal
      gcloud --project $PROJECT_ID compute instances list
      ```
1. Connect to your instance
   ```bash
   # In your workstation terminal
   gcloud --project=$PROJECT_ID beta compute ssh $INSTANCE_NAME
   ```
   * Do enter any value for a passphrase if prompted
1. Install `docker`
   ```bash
   # In your ssh session on the instance terminal
   sudo apt-get update
   sudo apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common
   curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add --
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian buster stable"
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io
   sudo usermod -a -G docker $USER
   ```
1. Install `docker-compose`
   ```bash
   # In your ssh session on the instance terminal
   sudo apt-get -y install wget
   sudo wget https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m) -O /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   docker-compose --version
   ```
1. Close the ssh connection to ensure the group modification is taken into account
   ```bash
   # In your ssh session on the instance terminal
   logout
   ```


### Install & start Airbyte
1. Connect to your instance
   ```bash
   # In your workstation terminal
   gcloud --project=$PROJECT_ID beta compute ssh $INSTANCE_NAME
   ```
1. In your command terminal, navigate to the folder you want to install everything in
   ```bash
   # In your ssh session on the instance terminal
   cd {{INSTALL_FOLDER}}
   ```
   * By default you will be in your user's home folder `~`, which may not be ideal if this is not a POC
1. Install Airbyte
   ```bash
   # In your ssh session on the instance terminal
   mkdir airbyte && cd airbyte
   wget https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}
   docker-compose up -d
   cd ..
   ```
   * the `-d` will make this docker container run in the background



### Install things needed to connect to a specific Airbyte Source or Destination

#### Google Cloud SQL Database
1. Navigate back to `{{INSTALL_FOLDER}}`
   ```bash
   # In your ssh session on the instance terminal
   cd {{INSTALL_FOLDER}}
   ```
1. Install Google Cloud CLI
   1. Follow these instructions https://cloud.google.com/sdk/docs/install-sdk#deb in your ssh session **with these changes**:
      1. For the `gcloud init` command
         1. For this prompt enter `1`
            ```
            Choose the account you would like to use to perform operations for this configuration:
               [1] {{GOOGLE_CLOUD_SERVICE_ACCOUNT'S_EMAIL_ADDRESS}}
               [2] Log in with a new account
            Please enter your numeric choice:  1
            ```
         1. For this prompt, enter `Y`
            ```
            API [cloudresourcemanager.googleapis.com] not enabled on project [{{PROJECT_NUMBER}}]. Would you like to enable and retry (this will take a few minutes)? (y/N)?  Y
            ```
1. Install what we need to run cloud_sql_proxy 
   1. Follow the instructions on based on https://cloud.google.com/sql/docs/postgres/connect-compute-engine#connect-gce-proxy in your ssh session **with these changes**
      1. Skip the `Open a terminal connection to your Compute Engine instance.` step, you are already connected
      1. **BEFORE** the `Install the Cloud SQL Auth proxy on the Compute Engine instance` step:
         1. Create a working directory
            ```bash
            # In your ssh session on the instance terminal
            mkdir proxy
            cd proxy
            ```
      1. **INSTEAD** of the `Start the Cloud SQL Auth proxy` step:
         1. Set up the Compute Engine instance to run cloud_sql_proxy as a service (based on https://www.jhanley.com/google-cloud-sql-proxy-installing-as-a-service-on-gce/)
            1. Create and open cloud-sql-proxy.service
               ```bash
               # In your ssh session on the instance terminal
               touch cloud-sql-proxy.service
               sudo nano cloud-sql-proxy.service
               ```
            1. Copy/paste this into cloud-sql-proxy.service
               ```
               [Unit]
               Description=Connecting PostgreSQL Client from Compute Engine using the Cloud SQL Proxy
               Documentation=https://cloud.google.com/sql/docs/postgresql/connect-compute-engine
               After=network.target

               [Service]
               WorkingDirectory={{INSTALL_FOLDER}}
               ExecStart={{INSTALL_FOLDER}}/cloud_sql_proxy -verbose=true -instances={{INSTANCE_CONNECTION_NAME}}=tcp:{{CLOUD_SQL_PORT_NUMBER}}
               Restart=always
               StandardOutput=journal
               User=root

               [Install]
               WantedBy=multi-user.target   
               ```
               1. Save the file `CTRL-S`
               1. Close the file `CTRL-X`
                  1. `Y`
                  1. ENTER
            1. Copy this file to /etc/systemd/system/cloud-sql-proxy.service
               ```bash
               # In your ssh session on the instance terminal
               sudo cp cloud-sql-proxy.service /etc/systemd/system/cloud-sql-proxy.service
               ```
            1. Enable the Cloud SQL Proxy to autostart when the Compute Engine starts
               ```bash
               # In your ssh session on the instance terminal
               sudo systemctl enable cloud-sql-proxy.service
               ```
            1. Start the service
               ```bash
               # In your ssh session on the instance terminal
               sudo systemctl daemon-reload
               sudo systemctl start cloud-sql-proxy
               ```
            1. Verify the service is running
               ```bash
               # In your ssh session on the instance terminal
               sudo systemctl status cloud-sql-proxy.service
               ```

##### Google Cloud SQL Postgres Database
1. Install the psql client
   ```bash
   # In your ssh session on the instance terminal
   sudo apt-get update
   sudo apt-get install postgresql-client
   ```


---


## Post-Initial Setup


### If the Compute Engine instance restarts
1. Open a command terminal & connect to the instance
   ```bash
   # In your workstation terminal
   gcloud config set project {{PROJECT_NAME}}
   PROJECT_ID=$(gcloud config get-value project)
   gcloud --project=$PROJECT_ID beta compute ssh {{COMPUTE_ENGINE_INSTANCE_NAME}}
   ```
   1. Do enter any value for a passphrase if prompted
1. Start Airbyte
   ```
   cd {{INSTALL_FOLDER}}/airbyte
   docker-compose up -d
   cd ..
   ```
   * the `-d` will make this docker container run in the background


#### To allow connections to a specific Airbyte Source or Destination

##### Google Cloud SQL Database
1. Start Cloud SQL Proxy
   1. Verify the service is running
      ```bash
      # In your ssh session on the instance terminal
      sudo systemctl status cloud-sql-proxy.service
      ```
      1. If it is not running
         ```bash
         # In your ssh session on the instance terminal
         sudo systemctl start cloud-sql-proxy
         ```



### Other instructions for connections to a specific Airbyte Source or Destination

#### Google Cloud SQL Database

##### To alter cloud-sql-proxy.service
1. Open a command terminal & connect to the instance
   ```bash
   # In your workstation terminal
   gcloud config set project {{PROJECT_NAME}}
   PROJECT_ID=$(gcloud config get-value project)
   gcloud --project=$PROJECT_ID beta compute ssh {{COMPUTE_ENGINE_INSTANCE_NAME}}
   ```
   1. Do enter any value for a passphrase if prompted
1. Open cloud-sql-proxy.service
   ```bash
   # In your ssh session on the instance terminal
   cd {{INSTALL_FOLDER}}/proxy
   sudo nano cloud-sql-proxy.service
   ```
1. Manually edit cloud-sql-proxy.service
   1. Save the file `CTRL-S`
   1. Close the file `CTRL-X`
      1. `Y`
      1. ENTER
1. Copy this file to /etc/systemd/system/cloud-sql-proxy.service
   ```bash
   # In your ssh session on the instance terminal
   sudo cp cloud-sql-proxy.service /etc/systemd/system/cloud-sql-proxy.service
   ```
1. Restart the service
   ```bash
   # In your ssh session on the instance terminal
   sudo systemctl daemon-reload
   sudo systemctl start cloud-sql-proxy
   ```
1. Verify the service is running
   ```bash
   # In your ssh session on the instance terminal
   sudo systemctl status cloud-sql-proxy.service
   ```


---

## Connect to Airbyte in the Compute Instance

:warning: For security reasons, we strongly recommend to not expose Airbyte publicly. Future versions will add support for SSL & Authentication.

1. Create ssh tunnel to your Compute Instance
   ```bash
   # In your workstation terminal
   gcloud --project=$PROJECT_ID beta compute ssh $INSTANCE_NAME -- -L 8000:localhost:8000 -N -f
   ```
   1. Do enter any value for a passphrase if prompted
   1. Notes
      1. Everything after the ` -- ` are SSH arguments
      1. `-L` = local (`-R` would be remote)
      1. `-N` = only forward ports
      1. `-f` = run SSH in the background
   1. If you get an error, try running the command without the ` -f` part, so you can see all of the messages
1. Visit [http://localhost:8000](http://localhost:8000) in your browser and start moving some data!
1. When you are finished with Airbyte, close the ssh connection:
   ```bash
   # In your ssh session on the instance terminal
   logout
   ```


---
   
## Key
* `{{CLOUD_SQL_PORT_NUMBER}}` = the port number you want to use to connect to the Cloud SQL databases, where host = `127.0.0.1`
* `{{COMPUTE_ENGINE_INSTANCE_NAME}}` = Name of the Google Cloud Compute Instance you created/are using
* `{{INSTALL_FOLDER}}` = Path of the folder on the Google Cloud Compute Instance where you are installing everything
* `{{INSTANCE_CONNECTION_NAME}}` = 
* `{{PROJECT_NAME}}` = Name of the Google Cloud Project where you created your Compute Engine instance
* `{{SERVICE_ACCOUNT_NAME}}` = Name of the Google Cloud Service Account you created/are using


## Troubleshooting

If you encounter any issues, just connect to our [Slack](https://slack.airbyte.io). Our community will help! We also have a [FAQ](../troubleshooting/on-deploying.md) section in our docs for common problems.

