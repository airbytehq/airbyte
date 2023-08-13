# Airbyte Pro

Airbyte Pro is a self-hosted version of Airbyte with additional features for enterprise customers. Airbyte Pro is currently in early development. Interested in Airbyte Pro for your organization? [Talk to sales](https://airbyte.com/company/talk-to-sales).

## Airbyte Pro License Key

A valid license key is required for Airbyte Pro. Talk to your Sales Representative to receive your license key before installing Airbyte Pro.

## Single Sign-On (SSO)

Airbyte Pro supports Single Sign-On, allowing an organization to manage user acces to their Airbyte Pro instance through the configuration of an Identity Provider (IdP).

Airbyte Pro currently supports SSO via OIDC with [Okta](https://www.okta.com/) as an IdP.

### Setting up Okta for SSO

You will need to create a new Okta OIDC App Integration for your Airbyte instance. Documentation on how to do this in Okta can be found [here](https://help.okta.com/en-us/Content/Topics/Apps/Apps_App_Integration_Wizard_OIDC.htm).

You should create an app integration with **OIDC - OpenID Connect** as the sign-in method and **Web Application** as the application type:

![Screenshot of Okta app integration creation modal](./assets/docs/okta-create-new-app-integration.png)

#### App integration name

Please choose a URL-friendly app integraiton name without spaces or special characters, such as `my-airbyte-app`:

![Screenshot of Okta app integration name](./assets/docs/okta-app-integration-name.png)

Spaces or special characters in this field could result in invalid redirect URIs.

#### Redirect URIs

In the **Login** section, set the following fields, substituting `<your-airbyte-domain>` and `<app-integration-name>` for your own values:

Sign-in redirect URIs:

```
<your-airbyte-domain>/auth/realms/airbyte/broker/<app-integration-name>/endpoint
```

Sign-out redirect URIs

```
<your-airbyte-domain>/auth/realms/airbyte/broker/<app-integration-name>/endpoint/logout_response
```

![Okta app integration name screenshot](./assets/docs/okta-login-redirect-uris.png)

_Example values_

`<your-airbyte-domain>` should point to where your Airbyte instance will be available, including the http/https protocol.

#### Deploying Airbyte Pro with Okta

Your Okta app is now set up and you're ready to deploy Airbyte with SSO! Take note of the following configuration values, as you will need them to configure Airbyte to use your new Okta SSO app integration:

- Okta domain ([how to find your Okta domain](https://developer.okta.com/docs/guides/find-your-domain/main/))
- App integration name
- Client ID
- Client Secret

Visit [Airbyte Pro deployment](/deploying-airbyte/on-kubernetes-via-helm#alpha-airbyte-pro-deployment) for instructions on how to deploy Airbyte Pro using `kubernetes`, `kubectl` and `helm`.
