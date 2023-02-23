import classNames from "classnames";
import { ReactNode } from "react";
import { FormattedMessage } from "react-intl";
import { Link } from "react-router-dom";

import { Card } from "components/ui/Card";
import { Text } from "components/ui/Text";

import { RoutePaths } from "pages/routePaths";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

import styles from "./NoDbtIntegration.module.scss";

export const NoDbtIntegration = () => {
  const workspaceId = useCurrentWorkspaceId();
  const dbtSettingsPath = `/${RoutePaths.Workspaces}/${workspaceId}/${RoutePaths.Settings}/dbt-cloud`;
  return (
    <Card
      title={
        <span className={styles.cardTitle}>
          <FormattedMessage id="connection.dbtCloudJobs.cardTitle" />
        </span>
      }
    >
      <div className={classNames(styles.cardBodyContainer)}>
        <Text className={styles.contextExplanation}>
          <FormattedMessage
            id="connection.dbtCloudJobs.noIntegration"
            values={{
              settingsLink: (linkText: ReactNode) => <Link to={dbtSettingsPath}>{linkText}</Link>,
            }}
          />
        </Text>
      </div>
    </Card>
  );
};
