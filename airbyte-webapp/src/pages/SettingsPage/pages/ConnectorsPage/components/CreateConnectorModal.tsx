import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LabeledInput } from "components";
import { Button } from "components/ui/Button";
import { FlexContainer } from "components/ui/Flex";
import { Modal, ModalBody, ModalFooter } from "components/ui/Modal";
import { Text } from "components/ui/Text";

import { isCloudApp } from "utils/app";
import { links } from "utils/links";

import styles from "./CreateConnectorModal.module.scss";

export interface CreateConnectorModalProps {
  errorMessage?: string;
  onClose: () => void;
  onSubmit: (sourceDefinition: {
    name: string;
    documentationUrl: string;
    dockerImageTag: string;
    dockerRepository: string;
  }) => Promise<void>;
}
const validationSchema = yup.object().shape({
  name: yup.string().trim().required("form.empty.error"),
  documentationUrl: yup.string().trim().url("form.url.error").notRequired(),
  dockerImageTag: yup.string().trim().required("form.empty.error"),
  dockerRepository: yup.string().trim().required("form.empty.error"),
});

const Label: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  return (
    <Text as="span" bold size="lg" className={styles.label}>
      {children}
    </Text>
  );
};

const CreateConnectorModal: React.FC<CreateConnectorModalProps> = ({ onClose, onSubmit, errorMessage }) => {
  const { formatMessage } = useIntl();

  return (
    <Formik
      initialValues={{
        name: "",
        documentationUrl: "",
        dockerImageTag: "",
        dockerRepository: "",
      }}
      validationSchema={validationSchema}
      onSubmit={async (values, { setSubmitting }) => {
        await onSubmit(values);
        setSubmitting(false);
      }}
    >
      {({ isSubmitting, isValid, dirty }) => (
        <Modal onClose={onClose} title={<FormattedMessage id="admin.addNewConnector" />}>
          <Form>
            <ModalBody>
              <FlexContainer direction="column" gap="xl">
                <Text>
                  <FormattedMessage
                    id="admin.learnMore"
                    values={{
                      lnk: (lnk: React.ReactNode) => (
                        <a className={styles.docLink} target="_blank" href={links.docsLink} rel="noreferrer">
                          {lnk}
                        </a>
                      ),
                    }}
                  />
                </Text>
                <FlexContainer direction="column">
                  <Field name="name">
                    {({ field, meta }: FieldProps<string>) => (
                      <LabeledInput
                        {...field}
                        type="text"
                        placeholder={formatMessage({
                          id: "admin.connectorName.placeholder",
                        })}
                        label={
                          <Label>
                            <FormattedMessage id="admin.connectorName" />
                          </Label>
                        }
                        error={meta.touched && !!meta.error}
                        message={
                          meta.touched && meta.error ? (
                            <FormattedMessage id={meta.error} />
                          ) : (
                            <FormattedMessage id="form.empty.error" />
                          )
                        }
                      />
                    )}
                  </Field>
                  <Field name="dockerRepository">
                    {({ field, meta }: FieldProps<string>) => (
                      <LabeledInput
                        {...field}
                        type="text"
                        autoComplete="off"
                        placeholder={formatMessage({
                          id: "admin.dockerRepository.placeholder",
                        })}
                        label={
                          <Label>
                            <FormattedMessage
                              id={isCloudApp() ? "admin.dockerFullImageName" : "admin.dockerRepository"}
                            />
                          </Label>
                        }
                        error={meta.touched && !!meta.error}
                        message={
                          meta.touched && meta.error ? (
                            <FormattedMessage id={meta.error} />
                          ) : (
                            <FormattedMessage id="form.empty.error" />
                          )
                        }
                      />
                    )}
                  </Field>
                  <Field name="dockerImageTag">
                    {({ field, meta }: FieldProps<string>) => (
                      <LabeledInput
                        {...field}
                        type="text"
                        autoComplete="off"
                        placeholder={formatMessage({
                          id: "admin.dockerImageTag.placeholder",
                        })}
                        label={
                          <Label>
                            <FormattedMessage id="admin.dockerImageTag" />
                          </Label>
                        }
                        error={!!meta.error && meta.touched}
                        message={
                          meta.touched && meta.error ? (
                            <FormattedMessage id={meta.error} />
                          ) : (
                            <FormattedMessage id="form.empty.error" />
                          )
                        }
                      />
                    )}
                  </Field>
                  <Field name="documentationUrl">
                    {({ field, meta }: FieldProps<string>) => (
                      <LabeledInput
                        {...field}
                        type="text"
                        autoComplete="off"
                        placeholder={formatMessage({
                          id: "admin.documentationUrl.placeholder",
                        })}
                        label={
                          <Label>
                            <FormattedMessage id="admin.documentationUrl" />
                          </Label>
                        }
                        error={meta.touched && !!meta.error}
                        message={meta.error && <FormattedMessage id={meta.error} />}
                      />
                    )}
                  </Field>

                  {errorMessage && <div className={styles.errorMessage}>{errorMessage}</div>}
                </FlexContainer>
              </FlexContainer>
            </ModalBody>
            <ModalFooter>
              <Button onClick={onClose} type="button" variant="secondary" disabled={isSubmitting}>
                <FormattedMessage id="form.cancel" />
              </Button>
              <Button type="submit" disabled={isSubmitting || !dirty || !isValid} isLoading={isSubmitting}>
                <FormattedMessage id="form.add" />
              </Button>
            </ModalFooter>
          </Form>
        </Modal>
      )}
    </Formik>
  );
};

export default CreateConnectorModal;
