import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { LabeledInput } from "components/LabeledInput";
import { Button } from "components/ui/Button";

import { useSubmitDbtCloudIntegrationConfig } from "packages/cloud/services/dbtCloud";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

import styles from "./DbtCloudSettingsView.module.scss";

export const DbtCloudSettingsView: React.FC = () => {
  const { mutate: submitDbtCloudIntegrationConfig, isLoading } = useSubmitDbtCloudIntegrationConfig();
  return (
    <SettingsCard title={<FormattedMessage id="settings.integrationSettings.dbtCloudSettings" />}>
      <Content>
        <Formik
          initialValues={{
            serviceToken: "",
          }}
          onSubmit={({ serviceToken }) => submitDbtCloudIntegrationConfig(serviceToken)}
        >
          <Form>
            <Field name="serviceToken">
              {({ field }: FieldProps<string>) => (
                <LabeledInput
                  {...field}
                  label={<FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.serviceToken" />}
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
