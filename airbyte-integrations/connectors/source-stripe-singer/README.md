# Stripe Test Configuration

In order to test the Stripe source, you will need API credentials and the ability to create records within Stripe.

## Community Contributor

1. Create an empty account on Stripe. 
1. Create a file at `secrets/config.json` with the following format using your client secret and account id:
```
{
  "client_secret": "sk_XXXXXXXXXXX",
  "account_id": "acct_XXXXXXXX",
  "start_date": "2017-01-01T00:00:00Z"
}
```

## Airbyte Employee

1. Access the `Stripe Integration Test Config` secret on Rippling under the `Engineering` folder
1. Create a file with the contents at `secrets/config.json`

