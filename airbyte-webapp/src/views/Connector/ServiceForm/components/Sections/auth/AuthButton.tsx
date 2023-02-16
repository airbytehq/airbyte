import classnames from "classnames";
import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components";
import { Text } from "components/base/Text";

import { ConnectorSpecification } from "core/domain/connector";
import { ConnectorIds } from "utils/connectors";

import { useServiceForm } from "../../../serviceFormContext";
import styles from "./AuthButton.module.scss";
import GoogleAuthButton from "./GoogleAuthButton";
import { useFormikOauthAdapter } from "./useOauthFlowAdapter";

function isGoogleConnector(connectorDefinitionId: string): boolean {
  return (
    [
      ConnectorIds.Sources.GoogleAds,
      ConnectorIds.Sources.GoogleAnalyticsUniversalAnalytics,
      ConnectorIds.Sources.GoogleDirectory,
      ConnectorIds.Sources.GoogleSearchConsole,
      ConnectorIds.Sources.GoogleSheets,
      ConnectorIds.Sources.GoogleWorkspaceAdminReports,
      ConnectorIds.Sources.YouTubeAnalytics,
      ConnectorIds.Destinations.GoogleSheets,
      // TODO: revert me
      ConnectorIds.Sources.YouTubeAnalyticsBusiness,
      //
    ] as string[]
  ).includes(connectorDefinitionId);
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
  const { selectedService, authErrors, selectedConnector } = useServiceForm();
  const hasAuthError = Object.values(authErrors).includes("form.empty.error");

  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const { loading, done, run, hasRun } = useFormikOauthAdapter(selectedConnector!);

  if (!selectedConnector) {
    console.error("Entered non-auth flow while no connector is selected");
    return null;
  }

  const definitionId = ConnectorSpecification.id(selectedConnector);
  const Component = getButtonComponent(definitionId);

  const messageStyle = classnames(styles.message, {
    [styles.error]: hasAuthError,
    [styles.success]: !hasAuthError,
  });
  return (
    <div className={styles.authSectionRow}>
      <Component isLoading={loading} type="button" onClick={() => run()}>
        {done ? (
          <FormattedMessage id="connectorForm.reauthenticate" />
        ) : (
          <FormattedMessage id={getAuthenticateMessageId(definitionId)} values={{ connector: selectedService?.name }} />
        )}
      </Component>
      {done && hasRun && (
        <Text as="div" size="lg" className={messageStyle}>
          <FormattedMessage id="connectorForm.authenticate.succeeded" />
        </Text>
      )}
      {hasAuthError && (
        <Text as="div" size="lg" className={messageStyle}>
          <FormattedMessage id="connectorForm.authenticate.required" />
        </Text>
      )}
    </div>
  );
};
