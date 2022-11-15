import classnames from "classnames";
import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { ConnectorSpecification } from "core/domain/connector";

import { useConnectorForm } from "../../../connectorFormContext";
import { useAuthentication } from "../../../useAuthentication";
import styles from "./AuthButton.module.scss";
import GoogleAuthButton from "./GoogleAuthButton";
import { useFormikOauthAdapter } from "./useOauthFlowAdapter";

function isGoogleConnector(connectorDefinitionId: string): boolean {
  return [
    "253487c0-2246-43ba-a21f-5116b20a2c50", // google ads
    "eff3616a-f9c3-11eb-9a03-0242ac130003", // google analytics
    "d19ae824-e289-4b14-995a-0632eb46d246", // google directory
    "eb4c9e00-db83-4d63-a386-39cfa91012a8", // google search console
    "71607ba1-c0ac-4799-8049-7f4b90dd50f7", // google sheets source
    "a4cbd2d1-8dbe-4818-b8bc-b90ad782d12a", // google sheets destination
    "ed9dfefa-1bbc-419d-8c5e-4d78f0ef6734", // google workspace admin reports
    "afa734e4-3571-11ec-991a-1e0031268139", // YouTube analytics
    // TODO: revert me
    "78752073-6d96-447d-8a93-2b6953f3c787", // Youtube analytics Business
    //
  ].includes(connectorDefinitionId);
}

function getButtonComponent(connectorDefinitionId: string) {
  if (isGoogleConnector(connectorDefinitionId)) {
    return GoogleAuthButton;
  }
  return Button;
}

function getAuthenticateMessageId(connectorDefinitionId: string): string {
  if (isGoogleConnector(connectorDefinitionId)) {
    return "connectorForm.signInWithGoogle";
  }
  return "connectorForm.authenticate";
}

export const AuthButton: React.FC = () => {
  const { selectedConnectorDefinition, selectedConnectorDefinitionSpecification } = useConnectorForm();
  const { hiddenAuthFieldErrors } = useAuthentication();
  const authRequiredError = Object.values(hiddenAuthFieldErrors).includes("form.empty.error");

  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const { loading, done, run, hasRun } = useFormikOauthAdapter(selectedConnectorDefinitionSpecification!);

  if (!selectedConnectorDefinitionSpecification) {
    console.error("Entered non-auth flow while no connector is selected");
    return null;
  }

  const definitionId = ConnectorSpecification.id(selectedConnectorDefinitionSpecification);
  const Component = getButtonComponent(definitionId);

  const messageStyle = classnames(styles.message, {
    [styles.error]: authRequiredError,
    [styles.success]: !authRequiredError,
  });
  const buttonLabel = done ? (
    <FormattedMessage id="connectorForm.reauthenticate" />
  ) : (
    <FormattedMessage
      id={getAuthenticateMessageId(definitionId)}
      values={{ connector: selectedConnectorDefinition?.name }}
    />
  );
  return (
    <div className={styles.authSectionRow}>
      <Component isLoading={loading} type="button" onClick={run}>
        {buttonLabel}
      </Component>
      {done && hasRun && (
        <Text as="div" size="lg" className={messageStyle}>
          <FormattedMessage id="connectorForm.authenticate.succeeded" />
        </Text>
      )}
      {authRequiredError && (
        <Text as="div" size="lg" className={messageStyle}>
          <FormattedMessage id="connectorForm.authenticate.required" />
        </Text>
      )}
    </div>
  );
};
