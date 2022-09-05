import ConnectorCard from "components/ConnectorCard";
import { ConnectorCardProps } from "components/ConnectorCard/ConnectorCard";

import { SlickSlider } from "../Slider/SlickSlider";
import styles from "./FrequentlyUsedDestinations.module.scss";

interface FrequentlyUsedDestinationsProps {
  destinations: ConnectorCardProps[];
}

export const FrequentlyUsedDestinations = ({ destinations }: FrequentlyUsedDestinationsProps) => {
  return (
    <div className={styles.container}>
      <SlickSlider title="Most frequently used destinations">
        {destinations.map(({ connectionName, connectorName, icon, releaseStage }, index) => (
          <div key={index}>
            <div className={styles.card}>
              <ConnectorCard
                connectionName={connectionName}
                connectorName={connectorName}
                icon={icon}
                releaseStage={releaseStage}
              />
            </div>
          </div>
        ))}
      </SlickSlider>
    </div>
  );
};
