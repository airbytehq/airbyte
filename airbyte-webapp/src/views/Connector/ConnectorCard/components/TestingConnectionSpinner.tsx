import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { ProgressBar } from "components/ui/ProgressBar";

import styles from "./TestingConnectionSpinner.module.scss";

// Progress Bar runs 2min for checking connections
const PROGRESS_BAR_TIME = 60 * 2;

interface TestingConnectionSpinnerProps {
  isCancellable?: boolean;
  onCancelTesting?: () => void;
}

export const TestingConnectionSpinner: React.FC<TestingConnectionSpinnerProps> = ({
  isCancellable,
  onCancelTesting,
}) => (
  <div className={styles.container}>
    <ProgressBar runTime={PROGRESS_BAR_TIME} />
    {isCancellable && (
      <Button className={styles.button} variant="secondary" type="button" onClick={() => onCancelTesting?.()}>
        <FormattedMessage id="form.cancel" />
      </Button>
    )}
  </div>
);
