import React from "react";
import { useIntl } from "react-intl";

import { ConnectorCard } from "components";
import { SlickSlider } from "components/ui/SlickSlider";

import { ConnectorCard as ConnectorCardType } from "../../types";
import styles from "./FrequentlyUsedDestinationsCard.module.scss";

export interface FrequentlyUsedConnectorsCardProps {
  connectors: ConnectorCardType[];
  connectorType: "source" | "destination";
  onConnectorSelect: (id: string, connectorName: string) => void;
}

export const FrequentlyUsedConnectorsCard: React.FC<FrequentlyUsedConnectorsCardProps> = ({
  connectors,
  onConnectorSelect,
  connectorType,
}) => {
  const { formatMessage } = useIntl();

  if (!connectors?.length) {
    return null;
  }

  return (
    <div className={styles.container}>
      <SlickSlider
        title={formatMessage({
          id: `${connectorType}s.frequentlyUsed`,
        })}
      >
        {connectors.map(({ id, name, icon, releaseStage }, index) => (
          <button key={index} className={styles.card} onClick={() => onConnectorSelect(id, name)}>
            <ConnectorCard connectionName={name} icon={icon} releaseStage={releaseStage} fullWidth />
          </button>
        ))}
      </SlickSlider>
    </div>
  );
};
