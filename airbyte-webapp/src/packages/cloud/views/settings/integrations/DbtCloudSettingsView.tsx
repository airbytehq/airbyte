import { Field, FieldProps, Form, Formik } from "formik";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { LabeledInput } from "components/LabeledInput";
import { Button } from "components/ui/Button";

import { useSubmitDbtCloudIntegrationConfig } from "packages/cloud/services/dbtCloud";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

import styles from "./DbtCloudSettingsView.module.scss";

export const DbtCloudSettingsView: React.FC = () => {
  const { mutate: submitDbtCloudIntegrationConfig, isLoading } = useSubmitDbtCloudIntegrationConfig();
  const [hasValidationError, setHasValidationError] = useState<boolean>(false);
  const [validationErrorMessage, setValidationErrorMessage] = useState<string | null>(null);
  return (
    <SettingsCard title={<FormattedMessage id="settings.integrationSettings.dbtCloudSettings" />}>
      <Content>
        <Formik
          initialValues={{
            serviceToken: "",
          }}
          onSubmit={({ serviceToken }) => {
            setHasValidationError(false);
            return submitDbtCloudIntegrationConfig(serviceToken, {
              onError: (e) => {
                setHasValidationError(true);

                // I honestly don't know why I had to do this; for some reason, when I
                // gave a `TError` type argument to the upstream `useMutation`, I start
                // getting spurious "no matching overloads" errors.
                // eslint-disable-next-line
                setValidationErrorMessage((e as any)?.message?.replace("Internal Server Error: ", ""));
              },
              onSuccess: () => setValidationErrorMessage(null),
            });
          }}
        >
          <Form>
            <Field name="serviceToken">
              {({ field }: FieldProps<string>) => (
                <LabeledInput
                  {...field}
                  label={<FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.serviceToken" />}
                  error={hasValidationError}
                  message={validationErrorMessage}
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
      </Content>
    </SettingsCard>
  );
};
