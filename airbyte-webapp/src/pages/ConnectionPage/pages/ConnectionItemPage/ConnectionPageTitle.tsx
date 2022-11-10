import { faTrash } from "@fortawesome/free-solid-svg-icons";
import React, { useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate, useParams } from "react-router-dom";

import { InfoBox } from "components/ui/InfoBox";
import { StepsMenu } from "components/ui/StepsMenu";
import { Text } from "components/ui/Text";

import { ConnectionStatus } from "core/request/AirbyteClient";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";

import { ConnectionName } from "./ConnectionName";
import styles from "./ConnectionPageTitle.module.scss";
import { ConnectionSettingsRoutes } from "./ConnectionSettingsRoutes";
import { StatusMainInfo } from "./StatusMainInfo";

export const ConnectionPageTitle: React.FC = () => {
  const params = useParams<{ id: string; "*": ConnectionSettingsRoutes }>();
  const navigate = useNavigate();
  const currentStep = params["*"] || ConnectionSettingsRoutes.STATUS;

  const { connection } = useConnectionEditService();

  const steps = useMemo(() => {
    const steps = [
      {
        id: ConnectionSettingsRoutes.STATUS,
        name: <FormattedMessage id="sources.status" />,
      },
      {
        id: ConnectionSettingsRoutes.REPLICATION,
        name: <FormattedMessage id="connection.replication" />,
      },
      {
        id: ConnectionSettingsRoutes.TRANSFORMATION,
        name: <FormattedMessage id="connectionForm.transformation.title" />,
      },
    ];

    connection.status !== ConnectionStatus.deprecated &&
      steps.push({
        id: ConnectionSettingsRoutes.SETTINGS,
        name: <FormattedMessage id="sources.settings" />,
      });

    return steps;
  }, [connection.status]);

  const onSelectStep = useCallback(
    (id: string) => {
      if (id === ConnectionSettingsRoutes.STATUS) {
        navigate("");
      } else {
        navigate(id);
      }
    },
    [navigate]
  );

  return (
    <div className={styles.container}>
      {connection.status === ConnectionStatus.deprecated && (
        <InfoBox className={styles.connectionDeleted} icon={faTrash}>
          <FormattedMessage id="connection.connectionDeletedView" />
        </InfoBox>
      )}
      <Text as="div" centered bold className={styles.connectionTitle}>
        <FormattedMessage id="connection.title" />
      </Text>
      <ConnectionName />
      <div className={styles.statusContainer}>
        <StatusMainInfo />
      </div>
      <StepsMenu lightMode data={steps} onSelect={onSelectStep} activeStep={currentStep} />
    </div>
  );
};
