import React from "react";
import { useIntl } from "react-intl";

import { ConnectorCard } from "components";
import { Card } from "components/ui/Card";

import { DestinationConnectorCard } from "../../types";
import styles from "./StartWithDestinationCard.module.scss";

export interface StartWithDestinationProps {
  destination: DestinationConnectorCard | undefined;
  onDestinationSelect: (id: string) => void;
}

export const StartWithDestinationCard: React.FC<StartWithDestinationProps> = ({ destination, onDestinationSelect }) => {
  const { formatMessage } = useIntl();

  if (!destination) {
    return null;
  }
  const { icon, releaseStage, name, destinationDefinitionId } = destination;

  const connectorCardClickHandler = () => {
    onDestinationSelect(destinationDefinitionId);
  };

  return (
    <button className={styles.button} onClick={connectorCardClickHandler}>
      <Card>
        <div className={styles.connectorCardWrapper}>
          <ConnectorCard
            icon={icon}
            releaseStage={releaseStage}
            connectionName={formatMessage({ id: "destinations.dontHaveYourOwnDestination" })}
            connectorName={formatMessage({ id: "destinations.startWith" }, { name })}
            fullWidth
          />
        </div>
      </Card>
    </button>
  );
};
