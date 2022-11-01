import { Field, FieldProps, Formik } from "formik";
import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
// import styled from "styled-components";
import { useNavigate } from "react-router-dom";
import * as yup from "yup";

import { LabeledInput, Link, LoadingButton } from "components";

// import { useConfig } from "config";
// import { useExperiment } from "hooks/services/Experiment";
// import { FieldError } from "packages/cloud/lib/errors/FieldError";
// import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useAuthenticationService } from "../../../../services/auth/AuthSpecificationService";

// import CheckBoxControl from "../../components/CheckBoxControl";
import { RoutePaths } from "../../../routePaths";
import { BottomBlock, FieldItem, Form, RowFieldItem } from "../../components/FormComponents";
import styles from "./SignupForm.module.scss";
// import {AuthService} from "../../../../services/auth/AuthService";

interface FormValues {
  firstName: string;
  lastName: string;
  email: string;
  company: string;
  password: string;
  confirmPassword: string;
}

// const MarginBlock = styled.div`
//   margin-bottom: 15px;
// `;

export const FirstNameField: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <Field name="firstName">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={<FormattedMessage id="signup.firstName" />}
          placeholder={formatMessage({
            id: "signup.firstName.placeholder",
          })}
          type="text"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const LastNameField: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <Field name="lastName">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={<FormattedMessage id="signup.lastName" />}
          placeholder={formatMessage({
            id: "signup.lastName.placeholder",
          })}
          type="text"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const CompanyNameField: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <Field name="company">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={<FormattedMessage id="signup.companyName" />}
          placeholder={formatMessage({
            id: "signup.companyName.placeholder",
          })}
          type="text"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const EmailField: React.FC<{ label?: React.ReactNode }> = ({ label }) => {
  const { formatMessage } = useIntl();

  return (
    <Field name="email">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={label || <FormattedMessage id="signup.Email" />}
          placeholder={formatMessage({
            id: "signup.Email.placeholder",
          })}
          type="text"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const PasswordField: React.FC<{ label?: React.ReactNode }> = ({ label }) => {
  const { formatMessage } = useIntl();

  return (
    <Field name="password">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={label || <FormattedMessage id="signup.password" />}
          placeholder={formatMessage({
            id: "signup.password.placeholder",
          })}
          type="password"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

export const ConfirmPasswordField: React.FC<{ label?: React.ReactNode }> = ({ label }) => {
  const { formatMessage } = useIntl();

  return (
    <Field name="confirmPassword">
      {({ field, meta }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          label={label || <FormattedMessage id="signup.confirmPassword" />}
          placeholder={formatMessage({
            id: "signup.confirmPassword.placeholder",
          })}
          type="password"
          error={!!meta.error && meta.touched}
          message={meta.touched && meta.error && formatMessage({ id: meta.error })}
        />
      )}
    </Field>
  );
};

// export const NewsField: React.FC = () => {
//     const { formatMessage } = useIntl();
//     return (
//         <Field name="news">
//             {({ field, meta }: FieldProps<string>) => (
//                 <MarginBlock>
//                     <CheckBoxControl
//                         {...field}
//                         checked={!!field.value}
//                         checkbox
//                         label={<FormattedMessage id="login.subscribe" />}
//                         message={meta.touched && meta.error && formatMessage({ id: meta.error })}
//                     />
//                 </MarginBlock>
//             )}
//         </Field>
//     );
// };

// export const Disclaimer: React.FC = () => {
//     const config = useConfig();
//     return (
//         <div className={styles.disclaimer}>
//             <FormattedMessage
//                 id="login.disclaimer"
//                 values={{
//                     terms: (terms: React.ReactNode) => (
//                         <Link $clear target="_blank" href={config.links.termsLink} as="a">
//                             {terms}
//                         </Link>
//                     ),
//                     privacy: (privacy: React.ReactNode) => (
//                         <Link $clear target="_blank" href={config.links.privacyLink} as="a">
//                             {privacy}
//                         </Link>
//                     ),
//                 }}
//             />
//         </div>
//     );
// };

interface SignupButtonProps {
  isLoading: boolean;
  disabled: boolean;
  buttonMessageId?: string;
}

export const SignupButton: React.FC<SignupButtonProps> = ({
  isLoading,
  disabled,
  buttonMessageId = "signup.submitButton",
}) => (
  <LoadingButton className={styles.signUpButton} type="submit" isLoading={isLoading} disabled={disabled}>
    <FormattedMessage id={buttonMessageId} />
  </LoadingButton>
);

export const SignupFormStatusMessage: React.FC = ({ children }) => (
  <div className={styles.statusMessage}>{children}</div>
);

export const SignupForm: React.FC = () => {
  const signUp = useAuthenticationService();
  const navigate = useNavigate();

  // const showName = !useExperiment("authPage.signup.hideName", false);
  // const showCompanyName = !useExperiment("authPage.signup.hideCompanyName", false);

  const validationSchema = useMemo(() => {
    const shape = {
      email: yup.string().email("signup.email.error").required("email.empty.error"),
      password: yup.string().min(8, "signup.password.minLength").required("password.empty.error"),
      firstName: yup.string().min(2, "signup.firstName.minLength").required("firstName.empty.error"),
      lastName: yup.string().min(2, "signup.lastName.minLength").required("lastName.empty.error"),
      company: yup.string().min(2, "signup.companyName.minLength").required("companyName.empty.error"),
      confirmPassword: yup
        .string()
        .oneOf([yup.ref("password"), null], "signup.matchPassword")
        .min(8, `signup.confirmPassword.minLength`)
        .required("confirmPassword.empty.error"),
    };
    // Confirm password should match new password
    // if (showName) {
    //     shape.name = shape.name.required("form.empty.error");
    // }
    // if (showCompanyName) {
    //     shape.companyName = shape.companyName.required("form.empty.error");
    // }
    return yup.object().shape(shape);
  }, []);

  return (
    <Formik<FormValues>
      initialValues={{
        firstName: "",
        lastName: "",
        email: "",
        company: "",
        password: "",
        confirmPassword: "",
      }}
      validationSchema={validationSchema}
      onSubmit={
        async (values) => {
          signUp.create(values).then(() => {
            navigate(`/${RoutePaths.Onboarding}`);
          });
        }
        // .catch(() => {
        // console.log(err)
        // if (err instanceof FieldError) {
        //     setFieldError(err.field, err.message);
        // } else {
        //     setStatus(err.message);
        // }
        // })
      }
      validateOnBlur
      validateOnChange
    >
      {({ isValid, isSubmitting, status }) => (
        <Form className={styles.form}>
          {/* {(showName || showCompanyName) && (*/}
          <RowFieldItem>
            <FirstNameField />
            <LastNameField />
          </RowFieldItem>
          {/* )}*/}
          <FieldItem>
            <EmailField />
          </FieldItem>
          <FieldItem>
            <CompanyNameField />
          </FieldItem>
          <FieldItem>
            <PasswordField />
          </FieldItem>
          <FieldItem>
            <ConfirmPasswordField />
          </FieldItem>
          <BottomBlock>
            <SignupButton isLoading={isSubmitting} disabled={!isValid} />
            {status && <SignupFormStatusMessage>{status}</SignupFormStatusMessage>}
          </BottomBlock>
          <div className={styles.termsAndPrivacy}>
            <FormattedMessage id="signup.description" />
            <Link to="" className={styles.link}>
              <FormattedMessage id="signup.privacy" />
            </Link>
            <FormattedMessage id="signup.and" />
            <Link to="" className={styles.link}>
              <FormattedMessage id="signup.terms" />
            </Link>
          </div>
        </Form>
      )}
    </Formik>
  );
};
