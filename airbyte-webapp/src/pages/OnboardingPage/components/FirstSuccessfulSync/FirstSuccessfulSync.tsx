import React from "react";
import { FormattedMessage } from "react-intl";

import { Text } from "components/ui/Text";

import styles from "./FirstSuccessfulSync.module.scss";

export const FirstSuccessfulSync: React.FC = () => {
  return (
    <div className={styles.container} data-testid="firstSuccessfulSync">
      <Text as="h2" size="md" centered className={styles.completedSyncText}>
        <FormattedMessage id="onboarding.syncCompleted" />
      </Text>
      <img className={styles.rocket} src="/rocket.png" alt="" />
    </div>
  );
};
