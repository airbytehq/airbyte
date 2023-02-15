import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LabeledRadioButton } from "components";
import { FormikConnectionFormValues } from "components/connection/ConnectionForm/formConfig";
import { Button } from "components/ui/Button";
import { Input } from "components/ui/Input";
import { ModalBody, ModalFooter } from "components/ui/Modal";
import { Text } from "components/ui/Text";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";
import { links } from "utils/links";

import styles from "./DestinationNamespaceModal.module.scss";
import { ExampleSettingsTable } from "./ExampleSettingsTable";

const destinationNamespaceValidationSchema = yup.object().shape({
  namespaceDefinition: yup
    .string()
    .oneOf([NamespaceDefinitionType.destination, NamespaceDefinitionType.source, NamespaceDefinitionType.customformat])
    .required("form.empty.error"),
  namespaceFormat: yup.string().when("namespaceDefinition", {
    is: NamespaceDefinitionType.customformat,
    then: yup.string().trim().required("form.empty.error"),
  }),
});

export interface DestinationNamespaceFormValueType {
  namespaceDefinition: NamespaceDefinitionType;
  namespaceFormat: string;
}

interface DestinationNamespaceModalProps {
  initialValues: Pick<FormikConnectionFormValues, "namespaceDefinition" | "namespaceFormat">;
  onCloseModal: () => void;
  onSubmit: (values: DestinationNamespaceFormValueType) => void;
}

export const DestinationNamespaceModal: React.FC<DestinationNamespaceModalProps> = ({
  initialValues,
  onCloseModal,
  onSubmit,
}) => {
  const { formatMessage } = useIntl();

  return (
    <Formik
      initialValues={{
        namespaceDefinition: initialValues?.namespaceDefinition ?? NamespaceDefinitionType.destination,
        namespaceFormat: initialValues.namespaceFormat,
      }}
      enableReinitialize
      validateOnBlur
      validateOnChange
      validationSchema={destinationNamespaceValidationSchema}
      onSubmit={(values: DestinationNamespaceFormValueType) => {
        onCloseModal();
        onSubmit(values);
      }}
    >
      {({ dirty, isValid, errors, values }) => (
        <Form>
          <ModalBody className={styles.content} padded={false}>
            <div className={styles.actions}>
              <Field name="namespaceDefinition">
                {({ field }: FieldProps<string>) => (
                  <LabeledRadioButton
                    {...field}
                    className={styles.radioButton}
                    id="destinationNamespace.destination"
                    label={
                      <Text as="span">
                        <FormattedMessage id="connectionForm.modal.destinationNamespace.option.destination" />
                      </Text>
                    }
                    value={NamespaceDefinitionType.destination}
                    checked={field.value === NamespaceDefinitionType.destination}
                  />
                )}
              </Field>
              <Field name="namespaceDefinition">
                {({ field }: FieldProps<string>) => (
                  <LabeledRadioButton
                    {...field}
                    className={styles.radioButton}
                    id="destinationNamespace.source"
                    label={
                      <Text as="span">
                        <FormattedMessage id="connectionForm.modal.destinationNamespace.option.source" />
                      </Text>
                    }
                    value={NamespaceDefinitionType.source}
                    checked={field.value === NamespaceDefinitionType.source}
                  />
                )}
              </Field>
              <Field name="namespaceDefinition">
                {({ field }: FieldProps<string>) => (
                  <LabeledRadioButton
                    {...field}
                    className={styles.radioButton}
                    id="destinationNamespace.customFormat"
                    label={
                      <Text as="span">
                        <FormattedMessage id="connectionForm.modal.destinationNamespace.option.customFormat" />
                      </Text>
                    }
                    value={NamespaceDefinitionType.customformat}
                    checked={field.value === NamespaceDefinitionType.customformat}
                  />
                )}
              </Field>
              <div className={styles.input}>
                <Field name="namespaceFormat">
                  {({ field, meta }: FieldProps<string>) => (
                    <Input
                      {...field}
                      disabled={values.namespaceDefinition !== NamespaceDefinitionType.customformat}
                      placeholder={formatMessage({
                        id: "connectionForm.modal.destinationNamespace.input.placeholder",
                      })}
                      error={!!meta.error && meta.touched}
                    />
                  )}
                </Field>
                {!!errors.namespaceFormat && (
                  <Text className={styles.errorMessage} size="sm">
                    <FormattedMessage id={errors.namespaceFormat} defaultMessage={errors.namespaceFormat} />
                  </Text>
                )}
              </div>
            </div>
            <div className={styles.description}>
              <FormattedMessage
                id={`connectionForm.modal.destinationNamespace.option.${
                  values.namespaceDefinition === NamespaceDefinitionType.customformat
                    ? "customFormat"
                    : values.namespaceDefinition
                }.description`}
              />
              <Text className={styles.generalInfo}>
                <FormattedMessage id="connectionForm.modal.destinationNamespace.description" />
              </Text>
              <ExampleSettingsTable namespaceDefinitionType={values.namespaceDefinition} />
              <a className={styles.namespaceLink} href={links.namespaceLink} target="_blank" rel="noreferrer">
                <Text className={styles.text} size="xs">
                  <FormattedMessage id="connectionForm.modal.destinationNamespace.learnMore.link" />
                </Text>
              </a>
            </div>
          </ModalBody>
          <ModalFooter>
            <Button type="button" variant="secondary" onClick={onCloseModal}>
              <FormattedMessage id="form.cancel" />
            </Button>
            <Button type="submit" disabled={!dirty || !isValid}>
              <FormattedMessage id="form.apply" />
            </Button>
          </ModalFooter>
        </Form>
      )}
    </Formik>
  );
};
