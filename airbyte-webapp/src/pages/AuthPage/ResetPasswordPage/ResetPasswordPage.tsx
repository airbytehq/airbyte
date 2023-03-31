import React, { useState } from "react";

import HeadTitle from "components/HeadTitle";

import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";

import CheckEmailSuccessful from "./components/CheckEmailSuccessful";
import ForgotPasswordForm from "./components/ForgotPasswordForm";
import ResetPasswordForm from "./components/ResetPasswordForm";
import styles from "./ResetPasswordPage.module.scss";

enum ValidatStepsTypes {
  FORGOT_PASSWORD = "forgotPassword",
  CHECK_EMAIL = "checkEmail",
  RESET_PASSWORD = "resetPassword",
}

const ResetPasswordPage: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<string>(ValidatStepsTypes.FORGOT_PASSWORD);
  const [isSuccessful, setSuccessfulState] = useState<boolean>(false);

  const { push } = useRouter();

  const onSubmitForgotForm = () => {
    setSuccessfulState(true);
    setCurrentStep(ValidatStepsTypes.CHECK_EMAIL);
  };

  const onSubmitResetForm = () => {
    onBack();
  };

  const onBack = () => {
    push(`/${RoutePaths.Signin}`);
  };
  return (
    <div className={styles.container}>
      <HeadTitle titles={[{ id: "resetPassword.pageTitle" }]} />
      <div className={styles.formContainer}>
        <img src="/daspireLogo.svg" alt="logo" width={50} style={{ marginTop: "40px" }} />
        {currentStep === ValidatStepsTypes.FORGOT_PASSWORD && (
          <ForgotPasswordForm onSubmit={onSubmitForgotForm} isSuccessful={isSuccessful} />
        )}
        {currentStep === ValidatStepsTypes.CHECK_EMAIL && (
          <CheckEmailSuccessful onBack={onBack} email="joedoe@example.com" />
        )}
        {currentStep === ValidatStepsTypes.RESET_PASSWORD && <ResetPasswordForm onSubmit={onSubmitResetForm} />}
      </div>
    </div>
  );
};

export default ResetPasswordPage;
