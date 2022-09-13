import React from "react";
import { FormattedMessage } from "react-intl";

import { Text } from "components/base/Text";

import styles from "./FirstSuccessfulSync.module.scss";

export const FirstSuccessfulSync: React.FC = () => {
  return (
    <div className={styles.container}>
      <Text as="h3" size="md" centered className={styles.completedSyncText}>
        <FormattedMessage id="onboarding.syncCompleted" />
      </Text>
      <img className={styles.rocket} src="/rocket.png" alt="" />
    </div>
  );
};
