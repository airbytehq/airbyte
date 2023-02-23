import React from "react";

import Indicator from "components/Indicator";
import { ReleaseStageBadge } from "components/ReleaseStageBadge";
import { FlexContainer } from "components/ui/Flex";

import { ReleaseStage } from "core/request/AirbyteClient";
import { getIcon } from "utils/imageUtils";

import styles from "./ConnectorCell.module.scss";

interface ConnectorCellProps {
  connectorName: string;
  img?: string;
  hasUpdate?: boolean;
  releaseStage?: ReleaseStage;
}

const ConnectorCell: React.FC<ConnectorCellProps> = ({ connectorName, img, hasUpdate, releaseStage }) => {
  return (
    <FlexContainer alignItems="center" gap="lg">
      <Indicator hidden={!hasUpdate} />
      <div className={styles.iconContainer}>{getIcon(img)}</div>
      <div>{connectorName}</div>
      <ReleaseStageBadge small tooltip={false} stage={releaseStage} />
    </FlexContainer>
  );
};

export default ConnectorCell;
