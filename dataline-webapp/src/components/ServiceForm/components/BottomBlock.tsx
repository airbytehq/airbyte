import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Button from "../../Button";

type IProps = {
  formType: "source" | "destination" | "connection";
  isSubmitting: boolean;
  isValid: boolean;
  dirty: boolean;
};

const ButtonContainer = styled.div`
  margin-top: 34px;
  text-align: right;
`;

const BottomBlock: React.FC<IProps> = ({
  isSubmitting,
  isValid,
  dirty,
  formType
}) => {
  return (
    <ButtonContainer>
      <Button type="submit" disabled={isSubmitting || !isValid || !dirty}>
        <FormattedMessage id={`onboarding.${formType}SetUp.buttonText`} />
      </Button>
    </ButtonContainer>
  );
};

export default BottomBlock;
