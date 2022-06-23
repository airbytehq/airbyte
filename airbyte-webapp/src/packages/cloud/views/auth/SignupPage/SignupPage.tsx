import React from "react";
import { FormattedMessage } from "react-intl";

import HeadTitle from "components/HeadTitle";

import { SignupForm } from "./components/SignupForm";
import SpecialBlock from "./components/SpecialBlock";
import styles from "./SignupPage.module.scss";

interface SignupPageProps {
  title?: string;
  titleStyle?: React.CSSProperties;
}

const SignupPage: React.FC<SignupPageProps> = ({ title, titleStyle }) => {
  return (
    <div>
      <HeadTitle titles={[{ id: "login.signup" }]} />
      <h1 className={styles.title} style={titleStyle}>
        {title ? title : <FormattedMessage id="login.activateAccess" />}
      </h1>
      <SpecialBlock />
      <SignupForm />
    </div>
  );
};

export default SignupPage;
