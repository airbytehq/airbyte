import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { useDeleteModal } from "components/common/DeleteBlock/useDeleteModal";
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
  dirty: boolean;
  errorMessage?: React.ReactNode;
  isSubmitting: boolean;
  isTestConnectionInProgress?: boolean;
  isValid: boolean;
  onCancelClick: () => void;
  onCancelTesting?: () => void;
  onDelete?: () => Promise<void>;
  onRetestClick?: () => void;
  successMessage?: React.ReactNode;
}

const EditControls: React.FC<IProps> = ({
  dirty,
  errorMessage,
  isSubmitting,
  isTestConnectionInProgress,
  isValid,
  onCancelClick,
  onCancelTesting,
  onDelete,
  onRetestClick,
  successMessage,
}) => {
  const { unfinishedFlows, formType } = useConnectorForm();
  const { onDeleteButtonClick } = useDeleteModal({ type: formType, onDelete });
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
        {onDelete && (
          <Button type="button" variant="danger" onClick={onDeleteButtonClick} data-id="open-delete-modal">
            <FormattedMessage id={`tables.${formType}Delete`} />
          </Button>
        )}
        <div className={styles.buttonsContainer}>
          {dirty && (
            <>
              <Button
                className={styles.cancelButton}
                type="button"
                variant="secondary"
                disabled={isSubmitting || !dirty}
                onClick={onCancelClick}
              >
                <FormattedMessage id="form.cancel" />
              </Button>
              <Button type="submit" disabled={isSubmitting || !dirty || Object.keys(unfinishedFlows).length > 0}>
                <FormattedMessage id="form.saveChangesAndTest" />
              </Button>
            </>
          )}
          {!dirty && onRetestClick && (
            <Button type="button" onClick={onRetestClick} disabled={!isValid}>
              <FormattedMessage id={`form.${formType}Retest`} />
            </Button>
          )}
        </div>
      </Controls>
    </>
  );
};

export default EditControls;
