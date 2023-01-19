import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";

import styles from "./CreateControls.module.scss";
import { TestingConnectionError } from "./TestingConnectionError";
import { TestingConnectionSpinner } from "./TestingConnectionSpinner";
import TestingConnectionSuccess from "./TestingConnectionSuccess";

interface CreateControlProps {
  formType: "source" | "destination";
  /**
   * Called in case the user cancels the form - if not provided, no cancel button is rendered
   */
  onCancel?: () => void;
  /**
   * Called in case the user reset the form - if not provided, no reset button is rendered
   */
  onReset?: () => void;
  submitLabel?: string;
  isSubmitting: boolean;
  errorMessage?: React.ReactNode;
  connectionTestSuccess?: boolean;

  isTestConnectionInProgress: boolean;
  onCancelTesting?: () => void;
}

const CreateControls: React.FC<CreateControlProps> = ({
  isTestConnectionInProgress,
  isSubmitting,
  formType,
  connectionTestSuccess,
  errorMessage,
  onCancelTesting,
  onCancel,
  onReset,
  submitLabel,
}) => {
  if (isSubmitting) {
    return <TestingConnectionSpinner isCancellable={isTestConnectionInProgress} onCancelTesting={onCancelTesting} />;
  }

  if (connectionTestSuccess) {
    return <TestingConnectionSuccess />;
  }

  return (
    <div className={styles.controlContainer}>
      {errorMessage && <TestingConnectionError errorMessage={errorMessage} />}
      {onReset && (
        <div className={styles.deleteButtonContainer}>
          <Button onClick={onReset} type="button" variant="danger">
            <FormattedMessage id="form.reset" />
          </Button>
        </div>
      )}
      <div className={styles.buttonContainer}>
        {onCancel && (
          <Button onClick={onCancel} type="button" variant="secondary">
            <FormattedMessage id="form.cancel" />
          </Button>
        )}
        <Button type="submit">
          {submitLabel || <FormattedMessage id={`onboarding.${formType}SetUp.buttonText`} />}
        </Button>
      </div>
    </div>
  );
};

export default CreateControls;
