import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";

import Label from "components/Label";
import LabeledToggle from "components/LabeledToggle";
import config from "config";
import FeedbackBlock from "../../../components/FeedbackBlock";

export type MetricsFormProps = {
  onSubmit: (data: { anonymousDataCollection: boolean }) => void;
  anonymousDataCollection?: boolean;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
};

const FormItem = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  min-height: 33px;
  margin-bottom: 10px;
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

const MetricsForm: React.FC<MetricsFormProps> = ({
  onSubmit,
  anonymousDataCollection,
  successMessage,
  errorMessage,
}) => {
  return (
    <Formik
      initialValues={{
        anonymousDataCollection: anonymousDataCollection || false,
      }}
      onSubmit={async (values) => {
        await onSubmit(values);
      }}
    >
      {({ isSubmitting, handleChange, handleSubmit }) => (
        <Form>
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
                  disabled={isSubmitting}
                  label={<FormattedMessage id="preferences.anonymizeData" />}
                  onChange={(event) => {
                    handleChange(event);
                    handleSubmit();
                  }}
                />
              )}
            </Field>
            <FeedbackBlock
              errorMessage={errorMessage}
              successMessage={successMessage}
              isLoading={isSubmitting}
            />
          </FormItem>
        </Form>
      )}
    </Formik>
  );
};

export default MetricsForm;
