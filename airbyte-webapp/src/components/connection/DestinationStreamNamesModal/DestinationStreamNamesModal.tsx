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
import { InfoTooltip } from "components/ui/Tooltip";

import styles from "./DestinationStreamNamesModal.module.scss";

export const enum StreamNameDefinitionValueType {
  Mirror = "mirror",
  Prefix = "prefix",
}

export interface DestinationStreamNamesFormValueType {
  streamNameDefinition: StreamNameDefinitionValueType;
  prefix: string;
}

const destinationStreamNamesValidationSchema = yup.object().shape({
  streamNameDefinition: yup
    .string()
    .oneOf([StreamNameDefinitionValueType.Mirror, StreamNameDefinitionValueType.Prefix])
    .required("form.empty.error"),
  prefix: yup.string().when("streamNameDefinition", {
    is: StreamNameDefinitionValueType.Prefix,
    then: yup.string().trim().required("form.empty.error"),
  }),
});

interface DestinationStreamNamesModalProps {
  initialValues: Pick<FormikConnectionFormValues, "prefix">;
  onCloseModal: () => void;
  onSubmit: (value: DestinationStreamNamesFormValueType) => void;
}

export const DestinationStreamNamesModal: React.FC<DestinationStreamNamesModalProps> = ({
  initialValues,
  onCloseModal,
  onSubmit,
}) => {
  const { formatMessage } = useIntl();

  return (
    <Formik
      initialValues={{
        streamNameDefinition: initialValues.prefix
          ? StreamNameDefinitionValueType.Prefix
          : StreamNameDefinitionValueType.Mirror,
        prefix: initialValues.prefix ?? "",
      }}
      enableReinitialize
      validateOnBlur
      validateOnChange
      validationSchema={destinationStreamNamesValidationSchema}
      onSubmit={(values: DestinationStreamNamesFormValueType) => {
        onCloseModal();
        onSubmit(values);
      }}
    >
      {({ dirty, isValid, errors, values }) => (
        <Form>
          <ModalBody className={styles.content} maxHeight={400} padded={false}>
            <Text className={styles.description}>
              <FormattedMessage id="connectionForm.modal.destinationStreamNames.description" />
            </Text>
            <Field name="streamNameDefinition">
              {({ field }: FieldProps<string>) => (
                <LabeledRadioButton
                  {...field}
                  className={styles.radioButton}
                  id="destinationStreamNames.mirror"
                  label={
                    <Text as="span">
                      <FormattedMessage id="connectionForm.modal.destinationStreamNames.radioButton.mirror" />
                    </Text>
                  }
                  value={StreamNameDefinitionValueType.Mirror}
                  checked={field.value === StreamNameDefinitionValueType.Mirror}
                />
              )}
            </Field>
            <Field name="streamNameDefinition">
              {({ field }: FieldProps<string>) => (
                <LabeledRadioButton
                  {...field}
                  className={styles.radioButton}
                  id="destinationStreamNames.prefix"
                  label={
                    <Text as="span">
                      <FormattedMessage id="connectionForm.modal.destinationStreamNames.radioButton.prefix" />
                      <InfoTooltip placement="top-start">
                        <FormattedMessage id="connectionForm.modal.destinationStreamNames.prefix.message" />
                      </InfoTooltip>
                    </Text>
                  }
                  value={StreamNameDefinitionValueType.Prefix}
                  checked={field.value === StreamNameDefinitionValueType.Prefix}
                />
              )}
            </Field>
            <div className={styles.input}>
              <Field name="prefix">
                {({ field, meta }: FieldProps<string>) => (
                  <Input
                    {...field}
                    disabled={values.streamNameDefinition !== StreamNameDefinitionValueType.Prefix}
                    placeholder={formatMessage({
                      id: "connectionForm.modal.destinationStreamNames.input.placeholder",
                    })}
                    error={!!meta.error && meta.touched}
                  />
                )}
              </Field>
              {!!errors.prefix && (
                <Text className={styles.errorMessage} size="sm">
                  <FormattedMessage id={errors.prefix} defaultMessage={errors.prefix} />
                </Text>
              )}
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
