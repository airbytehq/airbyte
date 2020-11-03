# Testing Source File

This integration 

## Necessary Credentials for tests

In order to run integrations tests in this connector, you need to:
1. Testing Google Cloud Service Storage
    1. Download and store your Google [Service Account](https://console.cloud.google.com/iam-admin/serviceaccounts) JSON file in `secrets/gcs.json`, it should look something like this:   
        ```
        {
            "type": "service_account",
            "project_id": "XXXXXXX",
            "private_key_id": "XXXXXXXX",
            "private_key": "-----BEGIN PRIVATE KEY-----\nXXXXXXXXXX\n-----END PRIVATE KEY-----\n",
            "client_email": "XXXXX@XXXXXX.iam.gserviceaccount.com",
            "client_id": "XXXXXXXXX",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/XXXXXXX0XXXXXX.iam.gserviceaccount.com"
        }

        ```
    1. Your Service Account should have [Storage Admin Rights](https://console.cloud.google.com/iam-admin/iam) (to create Buckets, read and store files in GCS)
     
1. Testing Amazon S3 
    1. Create a file at `secrets/aws.json`   
       ```
        {
            "aws_access_key_id": "XXXXXXX",
            "aws_secret_access_key": "XXXXXXX"
        }
       ```


