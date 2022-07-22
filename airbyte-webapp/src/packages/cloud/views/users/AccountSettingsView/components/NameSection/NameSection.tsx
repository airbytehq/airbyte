import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LoadingButton } from "components";
import { LabeledInput } from "components/LabeledInput";

import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { RowFieldItem } from "packages/cloud/views/auth/components/FormComponents";
import FeedbackBlock from "pages/SettingsPage/components/FeedbackBlock";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

import { useChangeName } from "./hooks";

const nameSectionValidationSchema = yup.object({
  name: yup.string().required("form.empty.error"),
});

export const NameSection: React.FC = () => {
  const { formatMessage } = useIntl();
  const user = useCurrentUser();
  const { changeName, successMessage, errorMessage } = useChangeName();

  return (
    <SettingsCard title={<FormattedMessage id="settings.account" />}>
      <Content>
        <Formik
          validateOnBlur
          validateOnChange
          validationSchema={nameSectionValidationSchema}
          initialValues={{
            name: user.name,
          }}
          onSubmit={(values, formikHelpers) =>
            changeName(values, formikHelpers).then(() => formikHelpers.resetForm({ values }))
          }
        >
          {({ isSubmitting, isValid, dirty }) => (
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
              <LoadingButton disabled={!isValid || !dirty} type="submit" isLoading={isSubmitting}>
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
