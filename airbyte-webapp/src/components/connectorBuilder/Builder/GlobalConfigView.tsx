import { useIntl } from "react-intl";

import { BuilderCard } from "./BuilderCard";
import { BuilderConfigView } from "./BuilderConfigView";
import { BuilderField } from "./BuilderField";
import { BuilderOneOf } from "./BuilderOneOf";
import { BuilderTitle } from "./BuilderTitle";
import styles from "./GlobalConfigView.module.scss";
import { UserInputField } from "./UserInputField";

export const GlobalConfigView: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <BuilderConfigView heading={formatMessage({ id: "connectorBuilder.globalConfiguration" })}>
      {/* Not using intl for the labels and tooltips in this component in order to keep maintainence simple */}
      <BuilderTitle path="global.connectorName" label="Connector Name" size="lg" />
      <BuilderCard className={styles.content}>
        <BuilderField type="string" path="global.urlBase" label="API URL" tooltip="Base URL of the source API" />
      </BuilderCard>
      <BuilderCard>
        <BuilderOneOf
          path="global.authenticator"
          label="Authentication"
          tooltip="Authentication method to use for requests sent to the API"
          options={[
            { label: "No Auth", typeValue: "NoAuth" },
            {
              label: "API Key",
              typeValue: "ApiKeyAuthenticator",
              default: {
                api_token: "{{ config['api_key'] }}",
              },
              children: (
                <>
                  <BuilderField
                    type="string"
                    path="global.authenticator.header"
                    label="Header"
                    tooltip="HTTP header which should be set to the API Key"
                  />
                  <UserInputField
                    label="API Key"
                    tooltip="The API key issued by the service. Fill it in in the user inputs"
                  />
                </>
              ),
            },
            {
              label: "Bearer",
              typeValue: "BearerAuthenticator",
              default: {
                api_token: "{{ config['api_key'] }}",
              },
              children: (
                <UserInputField
                  label="API Key"
                  tooltip="The API key issued by the service. Fill it in in the user inputs"
                />
              ),
            },
            {
              label: "Basic HTTP",
              typeValue: "BasicHttpAuthenticator",
              default: {
                username: "{{ config['username'] }}",
                password: "{{ config['password'] }}",
              },
              children: (
                <>
                  <UserInputField
                    label="Username"
                    tooltip="The username for the login. Fill it in in the user inputs"
                  />
                  <UserInputField
                    label="Password"
                    tooltip="The password for the login. Fill it in in the user inputs"
                  />
                </>
              ),
            },
          ]}
        />
      </BuilderCard>
    </BuilderConfigView>
  );
};
