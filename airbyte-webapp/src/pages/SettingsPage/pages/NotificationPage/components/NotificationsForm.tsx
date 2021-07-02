import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";

import Label from "components/Label";
import LabeledToggle from "components/LabeledToggle";
import FeedbackBlock from "../../../components/FeedbackBlock";

export type NotificationsFormProps = {
  onSubmit: (data: { news: boolean; securityUpdates: boolean }) => void;
  preferencesValues: {
    news: boolean;
    securityUpdates: boolean;
  };
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
};

const FormItem = styled.div`
  margin-bottom: 10px;
`;

const Subtitle = styled(Label)`
  padding-bottom: 9px;
`;

const NotificationsForm: React.FC<NotificationsFormProps> = ({
  onSubmit,
  preferencesValues,
  successMessage,
  errorMessage,
}) => {
  return (
    <Formik
      initialValues={{
        news: preferencesValues?.news || false,
        securityUpdates: preferencesValues?.securityUpdates || false,
      }}
      validateOnBlur={true}
      validateOnChange={false}
      onSubmit={async (values) => {
        await onSubmit(values);
      }}
    >
      {({ isSubmitting, handleChange, handleSubmit }) => (
        <Form>
          <Subtitle>
            <FormattedMessage id="settings.emailNotifications" />
            <FeedbackBlock
              errorMessage={errorMessage}
              successMessage={successMessage}
              isLoading={isSubmitting}
            />
          </Subtitle>
          <FormItem>
            <Field name="securityUpdates">
              {({ field }: FieldProps<string>) => (
                <LabeledToggle
                  {...field}
                  disabled={isSubmitting}
                  label={<FormattedMessage id="settings.securityUpdates" />}
                  onChange={(event) => {
                    handleChange(event);
                    handleSubmit();
                  }}
                />
              )}
            </Field>
          </FormItem>

          <FormItem>
            <Field name="news">
              {({ field }: FieldProps<string>) => (
                <LabeledToggle
                  {...field}
                  disabled={isSubmitting}
                  label={<FormattedMessage id="settings.newsletter" />}
                  onChange={(event) => {
                    handleChange(event);
                    handleSubmit();
                  }}
                />
              )}
            </Field>
          </FormItem>
        </Form>
      )}
    </Formik>
  );
};

export default NotificationsForm;
