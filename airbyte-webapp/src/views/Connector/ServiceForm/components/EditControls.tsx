import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components/ui/Button";

import { useDeleteModal } from "../../../../components/DeleteBlock/useDeleteModal";
import { useServiceForm } from "../serviceFormContext";
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
  onDelete?: () => Promise<unknown>;
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
  onDelete,
}) => {
  const { onDeleteButtonClick } = useDeleteModal({ type: formType, onDelete });
  const { unfinishedFlows } = useServiceForm();

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
          <Button variant="danger" onClick={onDeleteButtonClick} data-id="open-delete-modal">
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
