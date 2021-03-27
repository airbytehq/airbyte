import React from "react";
import styled from "styled-components";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";
import * as yup from "yup";

import { BigButton } from "components/CenteredPageComponents";
import LabeledInput from "components/LabeledInput";
import Label from "components/Label";
import LabeledToggle from "components/LabeledToggle";
import config from "config";
import Feedback from "./components/Feedback";

export type PreferencesFormProps = {
  onSubmit: (data: {
    email: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => void;
  isEdit?: boolean;
  values?: {
    email?: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  };
  feedback?: {
    anonymousDataCollection?: string;
    news?: string;
    securityUpdates?: string;
  };
};

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
  email: yup.string().email("form.email.error"),
});

const PreferencesForm: React.FC<PreferencesFormProps> = ({
  onSubmit,
  isEdit,
  values,
  feedback,
}) => {
  const formatMessage = useIntl().formatMessage;

  return (
    <Formik
      initialValues={{
        email: values?.email || "",
        anonymousDataCollection: values?.anonymousDataCollection || false,
        news: values?.news || false,
        securityUpdates: values?.securityUpdates || false,
      }}
      validateOnBlur={true}
      validateOnChange={false}
      validationSchema={preferencesValidationSchema}
      onSubmit={async (values, { setSubmitting }) => {
        setSubmitting(false);
        onSubmit(values);
      }}
    >
      {({ isSubmitting, values, handleChange, setFieldValue, resetForm }) => (
        <Form>
          {!isEdit && (
            <FormItem>
              <Field name="email">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label={<FormattedMessage id="form.emailOptional" />}
                    placeholder={formatMessage({
                      id: "form.email.placeholder",
                    })}
                    type="text"
                    error={!!meta.error && meta.touched}
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
                    onChange={(event) => {
                      handleChange(event);
                      if (
                        field.value.length === 0 &&
                        event.target.value.length > 0
                      ) {
                        setFieldValue("securityUpdates", true);
                      } else if (
                        field.value.length > 0 &&
                        event.target.value.length === 0
                      ) {
                        resetForm();
                      }
                    }}
                  />
                )}
              </Field>
            </FormItem>
          )}

          <Subtitle>
            <FormattedMessage id="preferences.anonymizeUsage" />
          </Subtitle>
          <Text>
            <FormattedMessage
              id={"preferences.collectData"}
              values={{
                docs: (...docs: React.ReactNode[]) => (
                  <DocsLink target="_blank" href={config.ui.docsLink}>
                    {docs}
                  </DocsLink>
                ),
              }}
            />
          </Text>
          <FormItem>
            <Field name="anonymousDataCollection">
              {({ field }: FieldProps<string>) => (
                <LabeledToggle
                  {...field}
                  message={
                    feedback?.anonymousDataCollection && (
                      <Feedback feedback={feedback.anonymousDataCollection} />
                    )
                  }
                  disabled={!values.email && !isEdit}
                  label={<FormattedMessage id="preferences.anonymizeData" />}
                  onChange={(event: React.ChangeEvent) => {
                    handleChange(event);
                    if (isEdit) {
                      onSubmit({
                        ...values,
                        anonymousDataCollection: !values.anonymousDataCollection,
                      });
                    }
                  }}
                />
              )}
            </Field>
          </FormItem>
          <Subtitle>
            <FormattedMessage id="preferences.news" />
          </Subtitle>
          <FormItem>
            <Field name="news">
              {({ field }: FieldProps<string>) => (
                <LabeledToggle
                  {...field}
                  disabled={!values.email && !isEdit}
                  label={<FormattedMessage id="preferences.featureUpdates" />}
                  message={
                    <>
                      <FormattedMessage id="preferences.unsubscribeAnyTime" />
                      {feedback?.news && <Feedback feedback={feedback.news} />}
                    </>
                  }
                  onChange={(event) => {
                    handleChange(event);
                    if (isEdit) {
                      onSubmit({
                        ...values,
                        news: !values.news,
                      });
                    }
                  }}
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
                <LabeledToggle
                  {...field}
                  message={
                    feedback?.securityUpdates && (
                      <Feedback feedback={feedback.securityUpdates} />
                    )
                  }
                  disabled={!values.email && !isEdit}
                  label={<FormattedMessage id="preferences.securityUpdates" />}
                  onChange={(event) => {
                    handleChange(event);
                    if (isEdit) {
                      onSubmit({
                        ...values,
                        securityUpdates: !values.securityUpdates,
                      });
                    }
                  }}
                />
              )}
            </Field>
          </FormItem>
          {!isEdit && (
            <ButtonContainer>
              <BigButton type="submit" disabled={isSubmitting}>
                <FormattedMessage id={"form.continue"} />
              </BigButton>
            </ButtonContainer>
          )}
        </Form>
      )}
    </Formik>
  );
};

export default PreferencesForm;
