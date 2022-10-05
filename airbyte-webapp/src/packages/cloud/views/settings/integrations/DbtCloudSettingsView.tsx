import { Field, FieldInputProps, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { LabeledInput } from "components/LabeledInput";
import { Button } from "components/ui/Button";
import { CollapsablePanel } from "components/ui/CollapsablePanel";

import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

import styles from "./DbtCloudSettingsView.module.scss";

const singleTenantUrlInput = (fieldProps: FieldInputProps<string>) => (
  <LabeledInput
    {...fieldProps}
    className={styles.singleTenantUrlInput}
    label={<FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.singleTenantUrl" />}
    type="text"
  />
);

export const DbtCloudSettingsView: React.FC = () => (
  <SettingsCard title={<FormattedMessage id="settings.integrationSettings.dbtCloudSettings" />}>
    <Content>
      <Formik
        initialValues={{
          serviceToken: "",
          singleTenantUrl: null,
        }}
        onSubmit={(values) => console.log(values)}
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
          <Field name="singleTenantUrl">
            {({ field }: FieldProps<string>) => (
              <CollapsablePanel
                className={styles.advancedOptions}
                closedClassName={styles.advancedOptionsClosed}
                openClassName={styles.advancedOptionsOpen}
                drawer={singleTenantUrlInput(field)}
              >
                <FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.advancedOptions" />
              </CollapsablePanel>
            )}
          </Field>
          <div className={styles.controlGroup}>
            <Button variant="secondary" className={styles.button}>
              <FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.testConnection" />
            </Button>
            <Button variant="primary" type="submit" className={styles.button}>
              <FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.submit" />
            </Button>
          </div>
        </Form>
      </Formik>
    </Content>
  </SettingsCard>
);
