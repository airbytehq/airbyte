import React from "react";
import { FormattedMessage } from "react-intl";

import { HeadTitle } from "components/common/HeadTitle";
import { Heading } from "components/ui/Heading";

import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";

import { OAuthLogin } from "../OAuthLogin";
import { Disclaimer, SignupForm } from "./components/SignupForm";
import SpecialBlock from "./components/SpecialBlock";
import styles from "./SignupPage.module.scss";

interface SignupPageProps {
  highlightStyle?: React.CSSProperties;
}

const SignupPage: React.FC<SignupPageProps> = ({ highlightStyle }) => {
  useTrackPage(PageTrackingCodes.SIGNUP);
  return (
    <div>
      <HeadTitle titles={[{ id: "login.signup" }]} />
      <Heading as="h1" size="xl" className={styles.title}>
        <FormattedMessage
          id="login.activateAccess"
          values={{
            hl: (hl: React.ReactNode) => (
              <span className={styles.highlight} style={highlightStyle}>
                {hl}
              </span>
            ),
          }}
        />
      </Heading>
      <SpecialBlock />
      <SignupForm />
      <OAuthLogin isSignUpPage />
      <Disclaimer />
    </div>
  );
};

export default SignupPage;
