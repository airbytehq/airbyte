import React from "react";
import { useIntl } from "react-intl";

import { ConnectorCard } from "components";
import { SlickSlider } from "components/ui/SlickSlider";

import styles from "./FrequentlyUsedConnectorsCard.module.scss";
import { FrequentlyUsedConnectorProps } from "./utils";

export interface FrequentlyUsedConnectorsCardProps {
  connectorType: "source" | "destination";
  connectors: FrequentlyUsedConnectorProps[];
  onClick: (id: string, connectorName: string) => void;
}

export const FrequentlyUsedConnectorsCard: React.FC<FrequentlyUsedConnectorsCardProps> = ({
  connectorType,
  connectors,
  onClick,
}) => {
  const { formatMessage } = useIntl();
  const titleIds = { source: "sources.suggested", destination: "destinations.suggested" };

  if (!connectors?.length) {
    return null;
  }

  return (
    <div className={styles.container}>
      <SlickSlider title={formatMessage({ id: titleIds[connectorType] })}>
        {connectors.map(({ id, name, icon, releaseStage }, index) => (
          <button key={index} className={styles.card} onClick={() => onClick(id, name)}>
            <ConnectorCard connectionName={name} icon={icon} releaseStage={releaseStage} fullWidth />
          </button>
        ))}
      </SlickSlider>
    </div>
  );
};
