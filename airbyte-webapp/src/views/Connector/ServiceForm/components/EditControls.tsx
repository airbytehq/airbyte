import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import { ButtonType } from "../../../../components/base/Button/types";
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
        <div>
          <Button
            type="submit"
            disabled={isSubmitting || !isValid || !dirty || Object.keys(unfinishedFlows).length > 0}
            label={<FormattedMessage id="form.saveChangesAndTest" />}
          />
          <ButtonContainer>
            <Button
              type="button"
              buttonType={ButtonType.Secondary}
              disabled={isSubmitting || !dirty}
              onClick={onCancelClick}
              label={<FormattedMessage id="form.cancel" />}
            />
          </ButtonContainer>
        </div>
        {onRetestClick && (
          <Button
            type="button"
            onClick={onRetestClick}
            disabled={!isValid}
            label={<FormattedMessage id={`form.${formType}Retest`} />}
          />
        )}
      </Controls>
    </>
  );
};

export default EditControls;
