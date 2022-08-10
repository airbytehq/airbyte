import React from "react";
import { FormattedMessage } from "react-intl";

import HeadTitle from "components/HeadTitle";

import { SignupForm } from "./components/SignupForm";
import SpecialBlock from "./components/SpecialBlock";
import styles from "./SignupPage.module.scss";

interface SignupPageProps {
  highlightStyle?: React.CSSProperties;
}

const SignupPage: React.FC<SignupPageProps> = ({ highlightStyle }) => {
  return (
    <div>
      <HeadTitle titles={[{ id: "login.signup" }]} />
      <h1 className={styles.title}>
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
      </h1>
      <SpecialBlock />
      <SignupForm />
    </div>
  );
};

export default SignupPage;
