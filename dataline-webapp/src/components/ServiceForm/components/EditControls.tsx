import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Button from "../../Button";

type IProps = {
  isSubmitting: boolean;
  isValid: boolean;
  dirty: boolean;
  resetForm: () => void;
  successMessage?: React.ReactNode;
};

const Controls = styled.div`
  margin-top: 34px;
`;

const ButtonContainer = styled.span`
  margin-left: 10px;
`;

const Success = styled(ButtonContainer)`
  color: ${({ theme }) => theme.successColor};
  font-size: 14px;
  line-height: 17px;
`;

const EditControls: React.FC<IProps> = ({
  isSubmitting,
  isValid,
  dirty,
  resetForm,
  successMessage
}) => {
  return (
    <Controls>
      <Button type="submit" disabled={isSubmitting || !isValid || !dirty}>
        <FormattedMessage id={`form.saveChanges`} />
      </Button>
      <ButtonContainer>
        <Button
          type="button"
          secondary
          disabled={isSubmitting || !isValid || !dirty}
          onClick={resetForm}
        >
          <FormattedMessage id={`form.cancel`} />
        </Button>
      </ButtonContainer>
      {successMessage && !dirty ? <Success>{successMessage}</Success> : null}
    </Controls>
  );
};

export default EditControls;
