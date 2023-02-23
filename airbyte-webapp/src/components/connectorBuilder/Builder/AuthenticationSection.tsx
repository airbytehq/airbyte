import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderFieldWithInputs } from "./BuilderFieldWithInputs";
import { BuilderOneOf } from "./BuilderOneOf";
import { BuilderOptional } from "./BuilderOptional";
import { KeyValueListField } from "./KeyValueListField";
import { inferredAuthValues } from "../types";

export const AuthenticationSection: React.FC = () => {
  const analyticsService = useAnalyticsService();

  return (
    <BuilderCard>
      <BuilderOneOf
        path="global.authenticator"
        label="Authentication"
        tooltip="Authentication method to use for requests sent to the API"
        onSelect={(type) =>
          analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.AUTHENTICATION_METHOD_SELECT, {
            actionDescription: "Authentication method selected",
            auth_type: type,
          })
        }
        options={[
          { label: "No Auth", typeValue: "NoAuth" },
          {
            label: "API Key",
            typeValue: "ApiKeyAuthenticator",
            default: {
              ...inferredAuthValues("ApiKeyAuthenticator"),
              header: "",
            },
            children: (
              <>
                <BuilderFieldWithInputs
                  type="string"
                  path="global.authenticator.header"
                  label="Header"
                  tooltip="HTTP header which should be set to the API Key"
                />
                <BuilderField
                  type="string"
                  path="global.authenticator.api_token"
                  label="API Key"
                  tooltip="The API key issued by the service. Fill it in in the user inputs"
                  readOnly
                />
              </>
            ),
          },
          {
            label: "Bearer",
            typeValue: "BearerAuthenticator",
            default: {
              ...inferredAuthValues("BearerAuthenticator"),
            },
            children: (
              <BuilderField
                type="string"
                path="global.authenticator.api_token"
                label="API Key"
                tooltip="The API key issued by the service. Fill it in in the user inputs"
                readOnly
              />
            ),
          },
          {
            label: "Basic HTTP",
            typeValue: "BasicHttpAuthenticator",
            default: {
              ...inferredAuthValues("BasicHttpAuthenticator"),
            },
            children: (
              <>
                <BuilderField
                  type="string"
                  path="global.authenticator.username"
                  label="Username"
                  tooltip="The username for the login. Fill it in in the user inputs"
                  readOnly
                />
                <BuilderField
                  type="string"
                  path="global.authenticator.password"
                  label="Password"
                  tooltip="The password for the login. Fill it in in the user inputs"
                  readOnly
                />
              </>
            ),
          },
          {
            label: "OAuth",
            typeValue: "OAuthAuthenticator",
            default: {
              ...inferredAuthValues("OAuthAuthenticator"),
              refresh_request_body: [],
              token_refresh_endpoint: "",
            },
            children: (
              <>
                <BuilderFieldWithInputs
                  type="string"
                  path="global.authenticator.token_refresh_endpoint"
                  label="Token refresh endpoint"
                  tooltip="The URL to call to obtain a new access token"
                />
                <BuilderField
                  type="string"
                  path="global.authenticator.client_id"
                  label="Client ID"
                  tooltip="The OAuth client ID. Fill it in in the user inputs"
                  readOnly
                />
                <BuilderField
                  type="string"
                  path="global.authenticator.client_secret"
                  label="Client secret"
                  tooltip="The OAuth client secret. Fill it in in the user inputs"
                  readOnly
                />
                <BuilderField
                  type="string"
                  path="global.authenticator.refresh_token"
                  label="Refresh token"
                  tooltip="The OAuth refresh token. Fill it in in the user inputs"
                  readOnly
                />
                <BuilderOptional>
                  <BuilderField
                    type="array"
                    path="global.authenticator.scopes"
                    optional
                    label="Scopes"
                    tooltip="Scopes to request"
                  />
                  <BuilderFieldWithInputs
                    type="string"
                    path="global.authenticator.token_expiry_date_format"
                    optional
                    label="Token expiry date format"
                    tooltip="The format of the expiry date of the access token as obtained from the refresh endpoint"
                  />
                  <BuilderFieldWithInputs
                    type="string"
                    path="global.authenticator.expires_in_name"
                    optional
                    label="Token expiry property name"
                    tooltip="The name of the property which contains the token exipiry date in the response from the token refresh endpoint"
                  />
                  <BuilderFieldWithInputs
                    type="string"
                    path="global.authenticator.access_token_name"
                    optional
                    label="Access token property name"
                    tooltip="The name of the property which contains the access token in the response from the token refresh endpoint"
                  />
                  <BuilderFieldWithInputs
                    type="string"
                    path="global.authenticator.grant_type"
                    optional
                    label="Grant type"
                    tooltip="The grant type to request for access_token"
                  />
                  <KeyValueListField
                    path="global.authenticator.refresh_request_body"
                    label="Request Parameters"
                    tooltip="The request body to send in the refresh request"
                  />
                </BuilderOptional>
              </>
            ),
          },
          {
            label: "Session token",
            typeValue: "SessionTokenAuthenticator",
            default: {
              ...inferredAuthValues("SessionTokenAuthenticator"),
            },
            children: (
              <>
                <BuilderFieldWithInputs
                  type="string"
                  path="global.authenticator.header"
                  label="Header"
                  tooltip="Specific HTTP header of source API for providing session token"
                />
                <BuilderFieldWithInputs
                  type="string"
                  path="global.authenticator.session_token_response_key"
                  label="Session token response key"
                  tooltip="Key for retrieving session token from api response"
                />
                <BuilderFieldWithInputs
                  type="string"
                  path="global.authenticator.login_url"
                  label="Login url"
                  tooltip="Url for getting a specific session token"
                />
                <BuilderFieldWithInputs
                  type="string"
                  path="global.authenticator.validate_session_url"
                  label="Validate session url"
                  tooltip="Url to validate passed session token"
                />
                <BuilderField
                  type="string"
                  path="global.authenticator.username"
                  label="Username"
                  tooltip="The username for the login. Fill it in in the user inputs"
                  readOnly
                />
                <BuilderField
                  type="string"
                  path="global.authenticator.password"
                  label="Password"
                  tooltip="The password for the login. Fill it in in the user inputs"
                  readOnly
                />
                <BuilderField
                  type="string"
                  path="global.authenticator.session_token"
                  label="Session token"
                  tooltip="Session token generated by user (if provided, username and password are not required). Fill it in in the user inputs"
                  readOnly
                />
              </>
            ),
          },
        ]}
      />
    </BuilderCard>
  );
};
