import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components/ui/Button";

import { useConnectorForm } from "../connectorFormContext";
import styles from "./EditControls.module.scss";
import { TestingConnectionError } from "./TestingConnectionError";
import { TestingConnectionSpinner } from "./TestingConnectionSpinner";
import TestingConnectionSuccess from "./TestingConnectionSuccess";

const Controls = styled.div`
  margin-top: 34px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

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
  const { unfinishedFlows } = useConnectorForm();

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
      {renderStatusMessage()}
      <Controls>
        <div className={styles.buttonsContainer}>
          <Button type="submit" disabled={isSubmitting || !dirty || Object.keys(unfinishedFlows).length > 0}>
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
      </Controls>
    </>
  );
};

export default EditControls;
