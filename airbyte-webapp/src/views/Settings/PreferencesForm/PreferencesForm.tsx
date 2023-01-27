import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import Label from "components/Label";
import LabeledInput from "components/LabeledInput";
import { LabeledSwitch } from "components/LabeledSwitch";
import { Button } from "components/ui/Button";

import { useConfig } from "config";
import { links } from "utils/links";

import EditControls from "./components/EditControls";

export interface PreferencesFormProps {
  onSubmit: (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => void;
  isEdit?: boolean;
  preferencesValues?: {
    email?: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  };
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
}

const ButtonContainer = styled.div`
  text-align: center;
  margin-top: 38px;
`;

const FormItem = styled.div`
  margin-bottom: 28px;
`;

const DocsLink = styled.a`
  text-decoration: none;
  color: ${({ theme }) => theme.primaryColor};
  cursor: pointer;
`;

const Subtitle = styled(Label)`
  padding-bottom: 9px;
`;

const Text = styled.div`
  font-style: normal;
  font-weight: normal;
  font-size: 13px;
  line-height: 150%;
  padding-bottom: 9px;
`;

const preferencesValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
});

const PreferencesForm: React.FC<PreferencesFormProps> = ({
  onSubmit,
  isEdit,
  preferencesValues,
  successMessage,
  errorMessage,
}) => {
  const { formatMessage } = useIntl();
  const config = useConfig();

  return (
    <Formik
      initialValues={{
        email: preferencesValues?.email || "",
        anonymousDataCollection: preferencesValues?.anonymousDataCollection || !config.segment.enabled,
        news: preferencesValues?.news || false,
        securityUpdates: preferencesValues?.securityUpdates || false,
      }}
      validateOnBlur
      validateOnChange={false}
      validationSchema={preferencesValidationSchema}
      onSubmit={(values) => {
        onSubmit(values);
      }}
    >
      {({ isSubmitting, values, handleChange, setFieldValue, resetForm, isValid, dirty }) => (
        <Form>
          <FormItem>
            <Field name="email">
              {({ field, meta }: FieldProps<string>) => (
                <LabeledInput
                  {...field}
                  label={<FormattedMessage id="form.yourEmail" />}
                  placeholder={formatMessage({
                    id: "form.email.placeholder",
                  })}
                  type="text"
                  error={!!meta.error && meta.touched}
                  message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                  onChange={(event) => {
                    handleChange(event);
                    if (isEdit) {
                      return;
                    }
                    if (field.value.length === 0 && event.target.value.length > 0) {
                      setFieldValue("securityUpdates", true);
                    } else if (field.value.length > 0 && event.target.value.length === 0) {
                      resetForm();
                      setFieldValue("email", "");
                    }
                  }}
                />
              )}
            </Field>
          </FormItem>
          {config.segment.enabled && (
            <>
              <Subtitle>
                <FormattedMessage id="preferences.anonymizeUsage" />
              </Subtitle>
              <Text>
                <FormattedMessage
                  id="preferences.collectData"
                  values={{
                    docs: (docs: React.ReactNode) => (
                      <DocsLink target="_blank" href={links.docsLink}>
                        {docs}
                      </DocsLink>
                    ),
                  }}
                />
              </Text>
              <FormItem>
                <Field name="anonymousDataCollection">
                  {({ field }: FieldProps<string>) => (
                    <LabeledSwitch
                      {...field}
                      disabled={!values.email}
                      label={<FormattedMessage id="preferences.anonymizeData" />}
                    />
                  )}
                </Field>
              </FormItem>
            </>
          )}
          <Subtitle>
            <FormattedMessage id="preferences.news" />
          </Subtitle>
          <FormItem>
            <Field name="news">
              {({ field }: FieldProps<string>) => (
                <LabeledSwitch
                  {...field}
                  disabled={!values.email}
                  label={<FormattedMessage id="preferences.featureUpdates" />}
                  message={<FormattedMessage id="preferences.unsubscribeAnyTime" />}
                />
              )}
            </Field>
          </FormItem>
          <Subtitle>
            <FormattedMessage id="preferences.security" />
          </Subtitle>
          <FormItem>
            <Field name="securityUpdates">
              {({ field }: FieldProps<string>) => (
                <LabeledSwitch
                  {...field}
                  disabled={!values.email}
                  label={<FormattedMessage id="preferences.securityUpdates" />}
                />
              )}
            </Field>
          </FormItem>
          {isEdit ? (
            <EditControls
              isSubmitting={isSubmitting}
              isValid={isValid}
              dirty={dirty}
              resetForm={resetForm}
              successMessage={successMessage}
              errorMessage={errorMessage}
            />
          ) : (
            <ButtonContainer>
              <Button size="lg" type="submit" disabled={isSubmitting}>
                <FormattedMessage id="form.continue" />
              </Button>
            </ButtonContainer>
          )}
        </Form>
      )}
    </Formik>
  );
};

export default PreferencesForm;
