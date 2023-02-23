import React from "react";
import { useIntl } from "react-intl";

import { ConnectorCard } from "components";
import { SlickSlider } from "components/ui/SlickSlider";

import styles from "./FrequentlyUsedConnectorsCard.module.scss";
import { SuggestedConnector } from "../../types";

export interface FrequentlyUsedConnectorsCardProps {
  connectors: SuggestedConnector[];
  connectorType: "source" | "destination";
  onConnectorSelect: (connectorDefinitionId: string, connectorName: string) => void;
}

export const FrequentlyUsedConnectorsCard: React.FC<FrequentlyUsedConnectorsCardProps> = ({
  connectors,
  onConnectorSelect,
  connectorType,
}) => {
  const { formatMessage } = useIntl();

  if (connectors.length === 0) {
    return null;
  }

  return (
    <div className={styles.container}>
      <SlickSlider
        title={formatMessage({
          id: `${connectorType}s.frequentlyUsed`,
        })}
      >
        {connectors.map(({ connectorDefinitionId, name, icon, releaseStage }, index) => (
          <button key={index} className={styles.card} onClick={() => onConnectorSelect(connectorDefinitionId, name)}>
            <ConnectorCard connectionName={name} icon={icon} releaseStage={releaseStage} fullWidth />
          </button>
        ))}
      </SlickSlider>
    </div>
  );
};
