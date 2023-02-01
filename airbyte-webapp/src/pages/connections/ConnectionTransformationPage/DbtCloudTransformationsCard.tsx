import React from "react";
import { FormattedMessage } from "react-intl";

import { Card } from "components/ui/Card";
import { Text } from "components/ui/Text";

import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { TrackErrorFn, useAppMonitoringService } from "hooks/services/AppMonitoringService";
import { useDbtIntegration, useAvailableDbtJobs } from "packages/cloud/services/dbtCloud";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

import styles from "./DbtCloudTransformationsCard/DbtCloudTransformationsCard.module.scss";
import { DbtJobsForm } from "./DbtCloudTransformationsCard/DbtJobsForm";
import { NoDbtIntegration } from "./DbtCloudTransformationsCard/NoDbtIntegration";

interface DbtCloudErrorBoundaryProps {
  trackError: TrackErrorFn;
  workspaceId: string;
}

class DbtCloudErrorBoundary extends React.Component<React.PropsWithChildren<DbtCloudErrorBoundaryProps>> {
  state = { error: null, displayMessage: null };

  // TODO parse the error to determine if the source was the upstream network call to
  // the dbt Cloud API. If it is, extract the `user_message` field from dbt's error
  // response for display to user; if not, provide a more generic error message. If the
  // error was *definitely* not related to the dbt Cloud API, consider reraising it.
  static getDerivedStateFromError(error: Error) {
    // TODO I'm pretty sure I did not correctly mock the exact error response format.
    // eslint-disable-next-line
    const displayMessage = (error?.message as any)?.status?.user_message;
    return { error, displayMessage };
  }

  componentDidCatch(error: Error) {
    const { trackError, workspaceId } = this.props;
    trackError(error, { workspaceId });
  }

  render() {
    const { error, displayMessage } = this.state;
    if (error) {
      return (
        <Card
          title={
            <span className={styles.cardTitle}>
              <FormattedMessage id="connection.dbtCloudJobs.cardTitle" />
            </span>
          }
        >
          <Text centered className={styles.cardBodyContainer}>
            {displayMessage ? (
              <FormattedMessage id="connection.dbtCloudJobs.dbtError" values={{ displayMessage }} />
            ) : (
              <FormattedMessage id="connection.dbtCloudJobs.genericError" />
            )}
          </Text>
        </Card>
      );
    }

    return this.props.children;
  }
}

type DbtIntegrationCardContentProps = Omit<ReturnType<typeof useDbtIntegration>, "hasDbtIntegration">;

const DbtIntegrationCardContent = ({ saveJobs, isSaving, dbtCloudJobs }: DbtIntegrationCardContentProps) => {
  const availableDbtJobs = useAvailableDbtJobs();
  return (
    <DbtJobsForm
      saveJobs={saveJobs}
      isSaving={isSaving}
      dbtCloudJobs={dbtCloudJobs}
      availableDbtCloudJobs={availableDbtJobs}
    />
  );
};

export const DbtCloudTransformationsCard = ({ connection }: { connection: WebBackendConnectionRead }) => {
  // Possible render paths:
  // 1) IF the workspace has no dbt cloud account linked
  //    THEN show "go to your settings to connect your dbt Cloud Account" text
  //    and the "Don't have a dbt account?" hero/media element
  // 2) IF the workspace has a dbt cloud account linked...
  //   2.1) AND the connection has no saved dbt jobs (cf: operations)
  //        THEN show empty jobs list and the "+ Add transformation" button
  //   2.2) AND the connection has saved dbt jobs
  //        THEN show the jobs list and the "+ Add transformation" button

  const { hasDbtIntegration, isSaving, saveJobs, dbtCloudJobs } = useDbtIntegration(connection);
  const { trackError } = useAppMonitoringService();
  const workspaceId = useCurrentWorkspaceId();

  return hasDbtIntegration ? (
    <DbtCloudErrorBoundary trackError={trackError} workspaceId={workspaceId}>
      <DbtIntegrationCardContent saveJobs={saveJobs} isSaving={isSaving} dbtCloudJobs={dbtCloudJobs} />
    </DbtCloudErrorBoundary>
  ) : (
    <NoDbtIntegration />
  );
};
