### Using the existing User Account

1. Follow instructions [here](https://www.balbooa.com/gridbox-documentation/how-to-get-google-client-id-and-client-secret), to get `CLIENT_ID, CLIENT_SECRET and REDIRECTED_URI`
2. Source `Google Search Console` provides scripts to easy get User Account credentials:
   1. Go to the `connectors/google-search-console/credentials` directory.
   2. Fill the file `credentials.json` with your personal credentials from step 1.
   3. Run the `./get_credentials.sh` script and follow the instructions.
   4. Copy the `refresh_token` from the console.
