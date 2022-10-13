import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { Input, ControlLabels, DropDown, Button } from "components";

import { Values } from "../types";

const Buttons = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;

  & > button {
    margin-left: 5px;
  }
`;

const ControlLabelsWithMargin = styled(ControlLabels)`
  margin-bottom: 29px;
`;

const RequestButton = styled(Button)`
  min-width: 105px;
`;

interface ConnectorFormProps {
  onSubmit: (values: Values) => void;
  onCancel: () => void;
  currentValues?: Values;
  hasFeedback?: boolean;
}

const requestConnectorValidationSchema = yup.object().shape({
  connectorType: yup.string().required("form.empty.error"),
  name: yup.string().required("form.empty.error"),
  additionalInfo: yup.string(),
  email: yup.string().email("form.email.error").required("form.empty.error"),
});

const ConnectorForm: React.FC<ConnectorFormProps> = ({ onSubmit, onCancel, currentValues, hasFeedback }) => {
  const { formatMessage } = useIntl();
  const dropdownData = [
    { value: "source", label: <FormattedMessage id="connector.source" /> },
    {
      value: "destination",
      label: <FormattedMessage id="connector.destination" />,
    },
  ];

  return (
    <Formik
      initialValues={{
        connectorType: currentValues?.connectorType || "",
        name: currentValues?.name || "",
        additionalInfo: currentValues?.additionalInfo || "",
        email: currentValues?.email || "",
      }}
      validateOnBlur
      validateOnChange
      validationSchema={requestConnectorValidationSchema}
      onSubmit={onSubmit}
    >
      {({ setFieldValue }) => (
        <Form>
          <Field name="connectorType">
            {({ field, meta }: FieldProps<string>) => (
              <ControlLabelsWithMargin
                error={!!meta.error && meta.touched}
                label={<FormattedMessage id="connector.type" />}
                message={!!meta.error && meta.touched && <FormattedMessage id={meta.error} />}
              >
                <DropDown
                  {...field}
                  options={dropdownData}
                  placeholder={formatMessage({
                    id: "connector.type.placeholder",
                  })}
                  error={!!meta.error && meta.touched}
                  onChange={(item) => {
                    setFieldValue("connectorType", item.value);
                  }}
                />
              </ControlLabelsWithMargin>
            )}
          </Field>
          <Field name="name">
            {({ field, meta, form }: FieldProps<string, Values>) => (
              <ControlLabelsWithMargin
                error={!!meta.error && meta.touched}
                label={
                  form.values.connectorType === "destination" ? (
                    <FormattedMessage id="connector.requestConnector.destination.name" />
                  ) : (
                    <FormattedMessage id="connector.requestConnector.source.name" />
                  )
                }
              >
                <Input {...field} error={!!meta.error && meta.touched} type="text" />
              </ControlLabelsWithMargin>
            )}
          </Field>
          <Field name="additionalInfo">
            {({ field, meta }: FieldProps<string>) => (
              <ControlLabelsWithMargin
                error={!!meta.error && meta.touched}
                label={<FormattedMessage id="connector.additionalInfo" />}
                message={<FormattedMessage id="connector.additionalInfo.message" />}
              >
                <Input {...field} type="text" error={!!meta.error && meta.touched} />
              </ControlLabelsWithMargin>
            )}
          </Field>
          {!currentValues?.email && (
            <Field name="email">
              {({ field, meta }: FieldProps<string>) => (
                <ControlLabelsWithMargin
                  error={!!meta.error && meta.touched}
                  label={<FormattedMessage id="connector.email" />}
                  message={!!meta.error && meta.touched && <FormattedMessage id={meta.error} />}
                >
                  <Input
                    {...field}
                    type="text"
                    error={!!meta.error && meta.touched}
                    placeholder={formatMessage({
                      id: "connector.email.placeholder",
                    })}
                  />
                </ControlLabelsWithMargin>
              )}
            </Field>
          )}
          <Buttons>
            <Button type="button" secondary onClick={onCancel} disabled={hasFeedback}>
              <FormattedMessage id="form.cancel" />
            </Button>
            <RequestButton type="submit" wasActive={hasFeedback}>
              {hasFeedback ? (
                <FormattedMessage id="connector.requested" />
              ) : (
                <FormattedMessage id="connector.request" />
              )}
            </RequestButton>
          </Buttons>
        </Form>
      )}
    </Formik>
  );
};

export default ConnectorForm;
