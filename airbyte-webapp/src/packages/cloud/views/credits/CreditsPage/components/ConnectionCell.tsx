import React from "react";

import { ConnectorIcon } from "components/common/ConnectorIcon";
import { ArrowRightIcon } from "components/icons/ArrowRightIcon";
import { Text } from "components/ui/Text";

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
    <>
      <div>
        <ConnectorIcon icon={sourceIcon} />
        <Text size="lg">{sourceDefinitionName}</Text>
      </div>
      <ArrowRightIcon />
      <div>
        <ConnectorIcon icon={destinationIcon} />
        <Text size="lg">{destinationDefinitionName}</Text>
      </div>
    </>
  );
};

export default ConnectionCell;
