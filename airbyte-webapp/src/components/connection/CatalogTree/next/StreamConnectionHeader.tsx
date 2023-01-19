import classnames from "classnames";
import { FormattedMessage } from "react-intl";

import { ArrowRightIcon } from "components/icons/ArrowRightIcon";
import { Heading } from "components/ui/Heading";

import { useNewTableDesignExperiment } from "hooks/connection/useNewTableDesignExperiment";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { getIcon } from "utils/imageUtils";

import styles from "./StreamConnectionHeader.module.scss";

export const renderIcon = (icon?: string): JSX.Element => <div className={styles.icon}>{getIcon(icon)}</div>;

export const StreamConnectionHeader: React.FC = () => {
  const {
    connection: { source, destination },
  } = useConnectionFormService();
  const isNewTableDesignEnabled = useNewTableDesignExperiment();
  const sourceStyles = classnames(styles.connector, styles.source);

  return (
    <div className={classnames(styles.container, { [styles.newTableContainer]: !!isNewTableDesignEnabled })}>
      <div className={sourceStyles}>
        {renderIcon(source.icon)}{" "}
        <Heading as="h5" size="sm">
          <FormattedMessage id="connectionForm.sourceTitle" />
        </Heading>
      </div>
      <div className={styles.destinationSection}>
        <div className={styles.arrowContainer}>
          <ArrowRightIcon />
        </div>
        <div className={classnames(styles.connector, styles.destination)}>
          {renderIcon(destination.icon)}{" "}
          <Heading as="h5" size="sm">
            <FormattedMessage id="connectionForm.destinationTitle" />
          </Heading>
        </div>
      </div>
    </div>
  );
};
