import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import { useServiceForm } from "../serviceFormContext";
import { TestingConnectionError } from "./TestingConnectionError";
import TestingConnectionSpinner from "./TestingConnectionSpinner";
import TestingConnectionSuccess from "./TestingConnectionSuccess";

const Controls = styled.div`
  margin-top: 34px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ButtonContainer = styled.span`
  margin-left: 10px;
`;

type IProps = {
  formType: "source" | "destination";
  isSubmitting: boolean;
  isValid: boolean;
  dirty: boolean;
  resetForm: () => void;
  onRetest?: () => void;
  onCancelTesting?: () => void;
  isTestConnectionInProgress?: boolean;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
};

const EditControls: React.FC<IProps> = ({
  isSubmitting,
  isTestConnectionInProgress,
  isValid,
  dirty,
  resetForm,
  formType,
  onRetest,
  successMessage,
  errorMessage,
  onCancelTesting,
}) => {
  const { unfinishedFlows } = useServiceForm();

  if (isSubmitting) {
    return <TestingConnectionSpinner isCancellable={isTestConnectionInProgress} onCancelTesting={onCancelTesting} />;
  }

  const showStatusMessage = () => {
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
      {showStatusMessage()}
      <Controls>
        <div>
          <Button
            type="submit"
            disabled={isSubmitting || !isValid || !dirty || Object.keys(unfinishedFlows).length > 0}
          >
            <FormattedMessage id="form.saveChangesAndTest" />
          </Button>
          <ButtonContainer>
            <Button type="button" secondary disabled={isSubmitting || !isValid || !dirty} onClick={resetForm}>
              <FormattedMessage id="form.cancel" />
            </Button>
          </ButtonContainer>
        </div>
        {onRetest && (
          <Button type="button" onClick={onRetest} disabled={!isValid}>
            <FormattedMessage id={`form.${formType}Retest`} />
          </Button>
        )}
      </Controls>
    </>
  );
};

export default EditControls;
