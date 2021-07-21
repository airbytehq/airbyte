import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Button } from "components";
import { useServiceForm } from "../serviceFormContext";
import TestingConnectionSpinner from "./TestingConnectionSpinner";
import TestingConnectionSuccess from "./TestingConnectionSuccess";
import TestingConnectionError from "./TestingConnectionError";

type IProps = {
  isSubmitting: boolean;
  isValid: boolean;
  dirty: boolean;
  resetForm: () => void;
  onRetest?: () => void;
  formType: "source" | "destination";
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
};

const Controls = styled.div`
  margin-top: 34px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`;

const ButtonContainer = styled.span`
  margin-left: 10px;
`;

const EditControls: React.FC<IProps> = ({
  isSubmitting,
  isValid,
  dirty,
  resetForm,
  formType,
  onRetest,
  successMessage,
  errorMessage,
}) => {
  const { unfinishedFlows } = useServiceForm();

  if (isSubmitting) {
    return <TestingConnectionSpinner />;
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
            disabled={
              isSubmitting ||
              !isValid ||
              !dirty ||
              Object.keys(unfinishedFlows).length > 0
            }
          >
            <FormattedMessage id="form.saveChangesAndTest" />
          </Button>
          <ButtonContainer>
            <Button
              type="button"
              secondary
              disabled={isSubmitting || !isValid || !dirty}
              onClick={resetForm}
            >
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
