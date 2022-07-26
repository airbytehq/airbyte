import React from "react";
import { FormattedMessage } from "react-intl";

import { H1 } from "components";
import HeadTitle from "components/HeadTitle";

import { SignupForm } from "./components/SignupForm";
import SpecialBlock from "./components/SpecialBlock";

const SignupPage: React.FC = () => {
  return (
    <div>
      <HeadTitle titles={[{ id: "login.signup" }]} />
      <H1 bold>
        <FormattedMessage id="login.activateAccess" />
      </H1>
      <SpecialBlock />
      <SignupForm />
    </div>
  );
};

export default SignupPage;
