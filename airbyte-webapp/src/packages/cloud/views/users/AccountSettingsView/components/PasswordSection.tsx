import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";
import { useMutation } from "react-query";
import styled from "styled-components";

import {
  Content,
  SettingsCard,
} from "pages/SettingsPage/pages/SettingsComponents";

import { Button } from "components/base/Button";
import { FieldItem } from "packages/cloud/views/auth/components/FormComponents";
import { GoogleAuthService } from "packages/cloud/lib/auth/GoogleAuthService";
import { LabeledInput } from "components/LabeledInput";
import { useAuth } from "packages/firebaseReact";

const ChangeEmailFooter = styled.div`
  display: flex;
  align-items: center;
  height: 50px;
`;

export const PasswordSection: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  const auth = useAuth();
  const authService = useMemo(() => new GoogleAuthService(() => auth), []);

  const { isLoading: isChangingPassword, mutate: changePassword } = useMutation<
    void,
    Error,
    { currentPassword: string; password: string }
  >(async ({ password, currentPassword }) => {
    return authService.changePassword(currentPassword, password);
  });

  return (
    <SettingsCard>
      <Content>
        <Formik
          initialValues={{
            currentPassword: "********",
            repeatPassword: "",
            password: "",
          }}
          onSubmit={({ password, currentPassword }, formikHelpers) => {
            changePassword({ password, currentPassword });
            formikHelpers.resetForm();
          }}
        >
          {({ values }) => (
            <Form>
              <FieldItem>
                <Field name="currentPassword">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.currentPassword" />
                      }
                      placeholder={formatMessage({
                        id: "login.password.placeholder",
                      })}
                      type="password"
                      error={!!meta.error && meta.touched}
                      message={
                        meta.touched &&
                        meta.error &&
                        formatMessage({ id: meta.error })
                      }
                    />
                  )}
                </Field>
              </FieldItem>
              <FieldItem>
                <Field name="password">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.password" />
                      }
                      placeholder={formatMessage({
                        id: "login.password.placeholder",
                      })}
                      type="password"
                      error={!!meta.error && meta.touched}
                      message={
                        meta.touched &&
                        meta.error &&
                        formatMessage({ id: meta.error })
                      }
                    />
                  )}
                </Field>
              </FieldItem>
              <FieldItem>
                <Field name="repeatPassword">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.repeatPassword" />
                      }
                      placeholder={formatMessage({
                        id: "login.password.placeholder",
                      })}
                      type="password"
                      error={!!meta.error && meta.touched}
                      message={
                        meta.touched &&
                        meta.error &&
                        formatMessage({ id: meta.error })
                      }
                    />
                  )}
                </Field>
              </FieldItem>
              <ChangeEmailFooter>
                <Button
                  isLoading={isChangingPassword}
                  type="submit"
                  disabled={
                    values.password !== values.repeatPassword ||
                    values.password.length === 0
                  }
                >
                  <FormattedMessage id="settings.accountSettings.updatePassword" />
                </Button>
              </ChangeEmailFooter>
            </Form>
          )}
        </Formik>
      </Content>
    </SettingsCard>
  );
};
