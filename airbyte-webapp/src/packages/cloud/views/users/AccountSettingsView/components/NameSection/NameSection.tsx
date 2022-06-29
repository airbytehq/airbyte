import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { LoadingButton } from "components";
import { LabeledInput } from "components/LabeledInput";

import { RowFieldItem } from "packages/cloud/views/auth/components/FormComponents";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

import { useName } from "./hooks";
import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import FeedbackBlock from "pages/SettingsPage/components/FeedbackBlock";

const NameSection: React.FC = () => {
  const { formatMessage } = useIntl();
  const user = useCurrentUser();
  const { changeName, successMessage, errorMessage } = useName();

  return (
    <SettingsCard title={<FormattedMessage id="settings.account" />}>
      <Content>
        <Formik
          initialValues={{
            name: user.name,
          }}
          onSubmit={changeName}
        >
          {({ isSubmitting }) => (
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
              <LoadingButton type="submit" isLoading={isSubmitting}>
                <FormattedMessage id="settings.accountSettings.updateName" />
              </LoadingButton>
              <FeedbackBlock errorMessage={errorMessage} successMessage={successMessage} isLoading={isSubmitting} />
            </Form>
          )}
        </Formik>
      </Content>
    </SettingsCard>
  );
};

export default NameSection;
