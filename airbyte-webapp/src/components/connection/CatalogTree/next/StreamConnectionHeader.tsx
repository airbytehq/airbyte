import classnames from "classnames";

import { ArrowRightIcon } from "components/icons/ArrowRightIcon";
import { Heading } from "components/ui/Heading";

import { useNewTableDesignExperiment } from "hooks/connection/useNewTableDesignExperiment";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

import styles from "./StreamConnectionHeader.module.scss";
import { ConnectorHeaderGroupIcon } from "./StreamDetailsPanel/StreamFieldsTable/ConnectorHeaderGroupIcon";

export const StreamConnectionHeader: React.FC = () => {
  const {
    connection: { source, destination },
  } = useConnectionFormService();
  const isNewTableDesignEnabled = useNewTableDesignExperiment();
  const sourceStyles = classnames(styles.connector, styles.source);

  return (
    <div className={classnames(styles.container, { [styles.newTableContainer]: !!isNewTableDesignEnabled })}>
      <div className={sourceStyles}>
        <Heading as="h5" size="sm">
          <ConnectorHeaderGroupIcon type="source" icon={source.icon} />
        </Heading>
      </div>
      <div className={styles.destinationSection}>
        <div className={styles.arrowContainer}>
          <ArrowRightIcon />
        </div>
        <div className={classnames(styles.connector, styles.destination)}>
          <Heading as="h5" size="sm">
            <ConnectorHeaderGroupIcon type="destination" icon={destination.icon} />
          </Heading>
        </div>
      </div>
    </div>
  );
};
