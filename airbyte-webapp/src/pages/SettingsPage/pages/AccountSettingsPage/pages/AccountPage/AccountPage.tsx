import { Field, FieldProps, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LabeledInput, LoadingButton } from "components";
import { FormChangeTracker } from "components/FormChangeTracker";

import { useUser } from "core/AuthContext";
import { useUniqueFormId } from "hooks/services/FormChangeTracker";
import { FieldItem, Form } from "pages/AuthPage/components/FormComponents";
import { useRoleOptions } from "services/roles/RolesService";

import styles from "./AccountPage.module.scss";

const validationSchema = yup.object().shape({
  firstName: yup.string().required("user.signupfirstName.empty.error"),
  lastName: yup.string().required("user.signuplastName.empty.error"),
});

const AccountPage: React.FC = () => {
  const { formatMessage } = useIntl();
  const formId = useUniqueFormId();
  const { user } = useUser();

  const roleLang = useRoleOptions().find((role) => role.value === user.role)?.label;

  const initialValues = {
    firstName: user.firstName,
    lastName: user.lastName,
    account: user.account,
    role: roleLang,
  };

  const onSubmit = () => {
    console.log("onSubmit");
  };

  return (
    <div className={styles.container}>
      <Formik
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={onSubmit}
        validateOnBlur
        validateOnChange
      >
        {({ isValid, dirty, isSubmitting }) => (
          <Form top="0">
            <FormChangeTracker changed={dirty} formId={formId} />
            <FieldItem bottom="30">
              <Field name="firstName">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    labelAdditionLength={0}
                    label={<FormattedMessage id="signup.firstName" />}
                    type="text"
                    error={!!meta.error && meta.touched}
                    message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  />
                )}
              </Field>
            </FieldItem>

            <FieldItem bottom="30">
              <Field name="lastName">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    labelAdditionLength={0}
                    label={<FormattedMessage id="signup.lastName" />}
                    type="text"
                    error={!!meta.error && meta.touched}
                    message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  />
                )}
              </Field>
            </FieldItem>

            <FieldItem bottom="30">
              <Field name="account">
                {({ field }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    labelAdditionLength={0}
                    label={<FormattedMessage id="login.yourEmail" />}
                    type="text"
                    disabled
                  />
                )}
              </Field>
            </FieldItem>

            <FieldItem bottom="30">
              <Field name="role">
                {({ field }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    labelAdditionLength={0}
                    label={<FormattedMessage id="user.addUserModal.role.fieldLabel" />}
                    type="text"
                    disabled
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

export default AccountPage;
