import React from "react";
import { FormattedMessage } from "react-intl";

import { SubmitButton, Title, SubTitle, EmailText } from "./common";

interface Iprops {
  onBack: () => void;
  email: string;
}

const CheckEmailForm: React.FC<Iprops> = ({ onBack, email }) => {
  return (
    <>
      <Title>
        <FormattedMessage id="resetPassword.check.title" />
      </Title>
      <SubTitle>
        <FormattedMessage id="resetPassword.check.explain" />
      </SubTitle>
      <EmailText>{email}</EmailText>
      <SubmitButton white type="button" onClick={onBack}>
        <FormattedMessage id="resetPassword.check.button" />
      </SubmitButton>
    </>
  );
};

export default CheckEmailForm;
