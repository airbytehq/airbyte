import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Button from "../../Button";
import Spinner from "../../Spinner";
import StatusIcon from "../../StatusIcon";

type IProps = {
  formType: "source" | "destination" | "connection";
  isSubmitting: boolean;
  hasSuccess?: boolean;
  isValid: boolean;
  dirty: boolean;
};

const ButtonContainer = styled.div`
  margin-top: 34px;
  text-align: right;
`;

const LoadingContainer = styled(ButtonContainer)`
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: ${({ theme }) => theme.darkPrimaryColor};
  display: flex;
  justify-content: center;
  align-items: center;
`;

const Loader = styled.div`
  margin-right: 10px;
`;

const Success = styled(StatusIcon)`
  width: 26px;
  height: 26px;
  padding-top: 5px;
  font-size: 17px;
`;

const BottomBlock: React.FC<IProps> = ({
  isSubmitting,
  isValid,
  dirty,
  formType,
  hasSuccess
}) => {
  if (hasSuccess) {
    return (
      <LoadingContainer>
        <Success success />
        <FormattedMessage id="form.successTests" />
      </LoadingContainer>
    );
  }

  if (isSubmitting) {
    return (
      <LoadingContainer>
        <Loader>
          <Spinner />
        </Loader>
        <FormattedMessage id="form.testingConnection" />
      </LoadingContainer>
    );
  }

  return (
    <ButtonContainer>
      <Button type="submit" disabled={!isValid || !dirty}>
        <FormattedMessage id={`onboarding.${formType}SetUp.buttonText`} />
      </Button>
    </ButtonContainer>
  );
};

export default BottomBlock;
