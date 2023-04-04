import { Field, FieldProps, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LabeledInput, LoadingButton } from "components";
import { FormChangeTracker } from "components/FormChangeTracker";

import { useUniqueFormId } from "hooks/services/FormChangeTracker";
import { FieldItem, Form } from "pages/AuthPage/components/FormComponents";

import styles from "./PasswordPage.module.scss";

const validationSchema = yup.object().shape({
  currentPassword: yup.string().required("settings.password.currentPassword.required"),
  newPassword: yup.string().required("settings.password.newPassword.required").min(8),
  confirmPassword: yup.string().required("settings.password.confirmPassword.required"),
});

const PasswordPage: React.FC = () => {
  const { formatMessage } = useIntl();
  const formId = useUniqueFormId();
  const onSubmit = () => {
    console.log("onSubmit");
  };

  return (
    <div className={styles.container}>
      <Formik
        initialValues={{
          currentPassword: "",
          newPassword: "",
          confirmPassword: "",
        }}
        validationSchema={validationSchema}
        onSubmit={onSubmit}
        validateOnBlur
        validateOnChange
      >
        {({ isValid, dirty, isSubmitting }) => (
          <Form top="0">
            <FormChangeTracker changed={dirty} formId={formId} />
            <FieldItem bottom="30">
              <Field name="currentPassword">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    labelAdditionLength={0}
                    label={<FormattedMessage id="settings.password.currentPassword" />}
                    type="password"
                    error={!!meta.error && meta.touched}
                    message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  />
                )}
              </Field>
            </FieldItem>

            <FieldItem bottom="30">
              <Field name="newPassword">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    labelAdditionLength={0}
                    label={<FormattedMessage id="settings.password.newPassword" />}
                    type="password"
                    error={!!meta.error && meta.touched}
                    message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  />
                )}
              </Field>
            </FieldItem>

            <FieldItem bottom="30">
              <Field name="confirmPassword">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    labelAdditionLength={0}
                    label={<FormattedMessage id="settings.password.confirmPassword" />}
                    type="password"
                    error={!!meta.error && meta.touched}
                    message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  />
                )}
              </Field>
            </FieldItem>

            <div className={styles.buttonContainer}>
              <LoadingButton white disabled={!(isValid && dirty)} size="lg" type="submit" isLoading={isSubmitting}>
                <FormattedMessage id="settings.password.button" />
              </LoadingButton>
            </div>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default PasswordPage;
