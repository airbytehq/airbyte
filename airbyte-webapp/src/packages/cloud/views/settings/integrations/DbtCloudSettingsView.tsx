import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { LabeledInput } from "components/LabeledInput";
import { Button } from "components/ui/Button";

import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

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
              <LabeledInput
                {...field}
                label={<FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.singleTenantUrl" />}
                type="text"
              />
            )}
          </Field>
          <Button variant="secondary">
            <FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.testConnection" />
          </Button>
          <Button variant="primary" type="submit">
            <FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.submit" />
          </Button>
        </Form>
      </Formik>
    </Content>
  </SettingsCard>
);
