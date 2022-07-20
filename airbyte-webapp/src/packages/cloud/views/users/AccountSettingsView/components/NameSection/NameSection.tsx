import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { LoadingButton } from "components";
import { LabeledInput } from "components/LabeledInput";

import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { RowFieldItem } from "packages/cloud/views/auth/components/FormComponents";
import FeedbackBlock from "pages/SettingsPage/components/FeedbackBlock";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

import { useChangeName } from "./hooks";
import { useValidation } from "./validation";

export const NameSection: React.FC = () => {
  const validate = useValidation();
  const { formatMessage } = useIntl();
  const user = useCurrentUser();
  const { changeName, successMessage, errorMessage } = useChangeName();

  return (
    <SettingsCard title={<FormattedMessage id="settings.account" />}>
      <Content>
        <Formik
          initialValues={{
            name: user.name,
          }}
          onSubmit={changeName}
          validate={validate}
        >
          {({ isSubmitting, isValid }) => (
            <Form>
              <RowFieldItem>
                <Field name="name">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={<FormattedMessage id="settings.accountSettings.name" />}
                      placeholder={formatMessage({
                        id: "settings.accountSettings.name.placeholder",
                      })}
                      type="text"
                      error={!!meta.error && meta.touched}
                      message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                    />
                  )}
                </Field>
              </RowFieldItem>
              <LoadingButton disabled={!isValid} type="submit" isLoading={isSubmitting}>
                <FormattedMessage id="settings.accountSettings.updateName" />
              </LoadingButton>
              <FeedbackBlock errorMessage={errorMessage} successMessage={successMessage} />
            </Form>
          )}
        </Formik>
      </Content>
    </SettingsCard>
  );
};
