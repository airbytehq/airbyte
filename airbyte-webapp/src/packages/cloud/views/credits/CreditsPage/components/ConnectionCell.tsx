import React from "react";

import { ConnectorIcon } from "components/common/ConnectorIcon";
import { ArrowRightIcon } from "components/icons/ArrowRightIcon";
import { FlexContainer, FlexItem } from "components/ui/Flex";
import { Text } from "components/ui/Text";

import styles from "./ConnectionCell.module.scss";

interface ConnectionCellProps {
  sourceDefinitionName: string;
  destinationDefinitionName: string;
  sourceIcon?: string;
  destinationIcon?: string;
}

const ConnectionCell: React.FC<ConnectionCellProps> = ({
  sourceDefinitionName,
  destinationDefinitionName,
  sourceIcon,
  destinationIcon,
}) => {
  return (
    <FlexContainer justifyContent="space-between">
      <FlexItem className={styles.connectorItem}>
        <FlexContainer direction="row" alignItems="center">
          <ConnectorIcon icon={sourceIcon} />
          <Text size="lg">{sourceDefinitionName}</Text>
        </FlexContainer>
      </FlexItem>
      <FlexItem className={styles.arrowItem}>
        <ArrowRightIcon />
      </FlexItem>
      <FlexItem className={styles.connectorItem}>
        <FlexContainer direction="row" alignItems="center">
          <ConnectorIcon icon={destinationIcon} />
          <Text size="lg">{destinationDefinitionName}</Text>
        </FlexContainer>
      </FlexItem>
    </FlexContainer>
  );
};

export default ConnectionCell;
