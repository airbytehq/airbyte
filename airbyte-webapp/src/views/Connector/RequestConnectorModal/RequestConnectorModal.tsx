import { Field, FieldProps, Form, Formik } from "formik";
import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { ControlLabels } from "components/LabeledControl";
import { Button } from "components/ui/Button";
import { DropDown } from "components/ui/DropDown";
import { Input } from "components/ui/Input";
import { ModalBody, ModalFooter } from "components/ui/Modal";

import useRequestConnector from "hooks/services/useRequestConnector";

import styles from "./RequestConnectorModal.module.scss";
import { Values } from "./types";

interface RequestConnectorModalProps {
  onClose: () => void;
  connectorType: "source" | "destination";
  workspaceEmail?: string;
  searchedConnectorName?: string;
}

const requestConnectorValidationSchema = yup.object().shape({
  connectorType: yup.string().required("form.empty.error"),
  name: yup.string().required("form.empty.error"),
  additionalInfo: yup.string(),
  email: yup.string().email("form.email.error").required("form.empty.error"),
});

const RequestConnectorModal: React.FC<RequestConnectorModalProps> = ({
  onClose,
  connectorType,
  searchedConnectorName,
  workspaceEmail,
}) => {
  const [hasFeedback, setHasFeedback] = useState(false);
  const { requestConnector } = useRequestConnector();

  const onSubmit = (values: Values) => {
    requestConnector(values);
    setHasFeedback(true);

    setTimeout(() => {
      setHasFeedback(false);
      onClose();
    }, 2000);
  };

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
        connectorType: connectorType || "",
        name: searchedConnectorName || "",
        additionalInfo: "",
        email: workspaceEmail || "",
      }}
      validateOnBlur
      validateOnChange
      validationSchema={requestConnectorValidationSchema}
      onSubmit={onSubmit}
    >
      {({ setFieldValue }) => (
        <Form>
          <ModalBody className={styles.modalBody}>
            <Field name="connectorType">
              {({ field, meta }: FieldProps<string>) => (
                <ControlLabels
                  className={styles.controlLabel}
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
                </ControlLabels>
              )}
            </Field>
            <Field name="name">
              {({ field, meta, form }: FieldProps<string, Values>) => (
                <ControlLabels
                  className={styles.controlLabel}
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
                </ControlLabels>
              )}
            </Field>
            <Field name="additionalInfo">
              {({ field, meta }: FieldProps<string>) => (
                <ControlLabels
                  className={styles.controlLabel}
                  error={!!meta.error && meta.touched}
                  label={<FormattedMessage id="connector.additionalInfo" />}
                  message={<FormattedMessage id="connector.additionalInfo.message" />}
                >
                  <Input {...field} type="text" error={!!meta.error && meta.touched} />
                </ControlLabels>
              )}
            </Field>
            {!workspaceEmail && (
              <Field name="email">
                {({ field, meta }: FieldProps<string>) => (
                  <ControlLabels
                    className={styles.controlLabel}
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
                  </ControlLabels>
                )}
              </Field>
            )}
          </ModalBody>

          <ModalFooter>
            <Button type="button" variant="secondary" onClick={onClose} disabled={hasFeedback}>
              <FormattedMessage id="form.cancel" />
            </Button>
            <Button className={styles.requestButton} type="submit" wasActive={hasFeedback}>
              {hasFeedback ? (
                <FormattedMessage id="connector.requested" />
              ) : (
                <FormattedMessage id="connector.request" />
              )}
            </Button>
          </ModalFooter>
        </Form>
      )}
    </Formik>
  );
};

export default RequestConnectorModal;
