import React from "react";
import { FormattedMessage } from "react-intl";

import { Text } from "components/base/Text";
import HeadTitle from "components/HeadTitle";

import { OAuthLogin } from "../OAuthLogin";
import { Disclaimer, SignupForm } from "./components/SignupForm";
import SpecialBlock from "./components/SpecialBlock";
import styles from "./SignupPage.module.scss";

interface SignupPageProps {
  highlightStyle?: React.CSSProperties;
}

const SignupPage: React.FC<SignupPageProps> = ({ highlightStyle }) => {
  return (
    <div>
      <HeadTitle titles={[{ id: "login.signup" }]} />
      <Text as="h1" size="xl" className={styles.title}>
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
      </Text>
      <SpecialBlock />
      <SignupForm />
      <OAuthLogin isSignUpPage />
      <Disclaimer />
    </div>
  );
};

export default SignupPage;
