import { faTrash } from "@fortawesome/free-solid-svg-icons";
import React, { useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate, useParams } from "react-router-dom";

import { ConnectionName } from "components/connection/ConnectionName";
import { InfoBox } from "components/ui/InfoBox";
import { StepsMenu } from "components/ui/StepsMenu";
import { Text } from "components/ui/Text";

import { ConnectionStatus } from "core/request/AirbyteClient";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";

import { ConnectionPageRoutePaths } from "../types";
import styles from "./ConnectionPageTitle.module.scss";
import { StatusMainInfo } from "./StatusMainInfo";

export const ConnectionPageTitle: React.FC = () => {
  const params = useParams<{ id: string; "*": ConnectionPageRoutePaths }>();
  const navigate = useNavigate();
  const currentStep = params["*"] || ConnectionPageRoutePaths.STATUS;

  const { connection } = useConnectionEditService();

  const steps = useMemo(() => {
    const steps = [
      {
        id: ConnectionPageRoutePaths.STATUS,
        name: <FormattedMessage id="sources.status" />,
      },
      {
        id: ConnectionPageRoutePaths.REPLICATION,
        name: <FormattedMessage id="connection.replication" />,
      },
      {
        id: ConnectionPageRoutePaths.TRANSFORMATION,
        name: <FormattedMessage id="connectionForm.transformation.title" />,
      },
    ];

    connection.status !== ConnectionStatus.deprecated &&
      steps.push({
        id: ConnectionPageRoutePaths.SETTINGS,
        name: <FormattedMessage id="sources.settings" />,
      });

    return steps;
  }, [connection.status]);

  const onSelectStep = useCallback(
    (id: string) => {
      if (id === ConnectionPageRoutePaths.STATUS) {
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
