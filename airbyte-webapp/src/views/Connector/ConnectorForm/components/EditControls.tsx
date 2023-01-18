import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";

import styles from "./EditControls.module.scss";
import { TestingConnectionError } from "./TestingConnectionError";
import { TestingConnectionSpinner } from "./TestingConnectionSpinner";
import TestingConnectionSuccess from "./TestingConnectionSuccess";

interface IProps {
  formType: "source" | "destination";
  isSubmitting: boolean;
  isValid: boolean;
  dirty: boolean;
  onCancelClick: () => void;
  onRetestClick?: () => void;
  onCancelTesting?: () => void;
  isTestConnectionInProgress?: boolean;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
}

const EditControls: React.FC<IProps> = ({
  isSubmitting,
  isTestConnectionInProgress,
  isValid,
  dirty,
  onCancelClick,
  formType,
  onRetestClick,
  successMessage,
  errorMessage,
  onCancelTesting,
}) => {
  if (isSubmitting) {
    return <TestingConnectionSpinner isCancellable={isTestConnectionInProgress} onCancelTesting={onCancelTesting} />;
  }

  const renderStatusMessage = () => {
    if (errorMessage) {
      return <TestingConnectionError errorMessage={errorMessage} />;
    }
    if (successMessage) {
      return <TestingConnectionSuccess />;
    }
    return null;
  };

  return (
    <>
      <div className={styles.controlsContainer}>
        <div className={styles.buttonsContainer}>
          <Button type="submit" disabled={isSubmitting || !dirty}>
            <FormattedMessage id="form.saveChangesAndTest" />
          </Button>
          <Button
            className={styles.cancelButton}
            type="button"
            variant="secondary"
            disabled={isSubmitting || !dirty}
            onClick={onCancelClick}
          >
            <FormattedMessage id="form.cancel" />
          </Button>
        </div>
        {onRetestClick && (
          <Button type="button" onClick={onRetestClick} disabled={!isValid}>
            <FormattedMessage id={`form.${formType}Retest`} />
          </Button>
        )}
      </div>
      {renderStatusMessage()}
    </>
  );
};

export default EditControls;
