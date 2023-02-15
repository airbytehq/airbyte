import { Field, FieldProps, Form, Formik } from "formik";
import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { LabeledInput } from "components/LabeledInput";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { useSubmitDbtCloudIntegrationConfig } from "packages/cloud/services/dbtCloud";
import { SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";
import { links } from "utils/links";

import styles from "./DbtCloudSettingsView.module.scss";

export const DbtCloudSettingsView: React.FC = () => {
  const { formatMessage } = useIntl();
  const { mutate: submitDbtCloudIntegrationConfig, isLoading } = useSubmitDbtCloudIntegrationConfig();
  const [hasValidationError, setHasValidationError] = useState(false);
  const [validationMessage, setValidationMessage] = useState("");
  return (
    <SettingsCard title={<FormattedMessage id="settings.integrationSettings.dbtCloudSettings" />}>
      <div className={styles.cardContent}>
        <Formik
          initialValues={{
            serviceToken: "",
          }}
          onSubmit={({ serviceToken }, { resetForm }) => {
            setHasValidationError(false);
            setValidationMessage("");
            return submitDbtCloudIntegrationConfig(serviceToken, {
              onError: (e) => {
                setHasValidationError(true);

                setValidationMessage(e.message.replace("Internal Server Error: ", ""));
              },
              onSuccess: () => {
                setValidationMessage(
                  formatMessage({ id: "settings.integrationSettings.dbtCloudSettings.form.success" })
                );
                resetForm();
              },
            });
          }}
        >
          <Form>
            <Text className={styles.description}>
              <FormattedMessage
                id="settings.integrationSettings.dbtCloudSettings.form.description"
                values={{
                  lnk: (node: React.ReactNode) => (
                    <a href={links.dbtCloudIntegrationDocs} target="_blank" rel="noreferrer">
                      {node}
                    </a>
                  ),
                }}
              />
            </Text>
            <Field name="serviceToken">
              {({ field }: FieldProps<string>) => (
                <LabeledInput
                  {...field}
                  label={<FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.serviceToken" />}
                  error={hasValidationError}
                  message={validationMessage}
                  type="text"
                />
              )}
            </Field>
            <div className={styles.controlGroup}>
              <Button variant="primary" type="submit" className={styles.button} isLoading={isLoading}>
                <FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.submit" />
              </Button>
            </div>
          </Form>
        </Formik>
      </div>
    </SettingsCard>
  );
};
