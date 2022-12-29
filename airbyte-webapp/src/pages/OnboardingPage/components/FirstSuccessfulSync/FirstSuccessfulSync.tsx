import React from "react";
import { FormattedMessage } from "react-intl";

import { Heading } from "components/ui/Heading";

import styles from "./FirstSuccessfulSync.module.scss";

export const FirstSuccessfulSync: React.FC = () => {
  return (
    <div className={styles.container} data-testid="firstSuccessfulSync">
      <Heading as="h2" centered className={styles.completedSyncText}>
        <FormattedMessage id="onboarding.syncCompleted" />
      </Heading>
      <img className={styles.rocket} src="/rocket.png" alt="" />
    </div>
  );
};
