import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";

import {
  Content,
  SettingsCard,
} from "pages/SettingsPage/pages/SettingsComponents";
import { FieldItem } from "packages/cloud/views/auth/components/FormComponents";
import { LabeledInput } from "components/LabeledInput";
import NotificationsForm from "pages/SettingsPage/pages/NotificationPage/components/NotificationsForm";
import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import useWorkspace from "hooks/services/useWorkspace";
import useWorkspaceEditor from "pages/SettingsPage/components/useWorkspaceEditor";

export const EmailSection: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const user = useCurrentUser();

  const { workspace } = useWorkspace();
  const {
    errorMessage,
    successMessage,
    loading,
    updateData,
  } = useWorkspaceEditor();

  const onChange = async (data: {
    news: boolean;
    securityUpdates: boolean;
  }) => {
    await updateData({ ...workspace, ...data });
  };
  return (
    <SettingsCard>
      <Content>
        <Formik
          initialValues={{
            email: user.email,
          }}
          onSubmit={() => {
            throw new Error("Not implemented");
          }}
        >
          {() => (
            <Form>
              <FieldItem>
                <Field name="email">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.accountSettings.email" />
                      }
                      disabled={true}
                      placeholder={formatMessage({
                        id: "login.yourEmail.placeholder",
                      })}
                      type="text"
                      error={!!meta.error && meta.touched}
                      message={
                        meta.touched &&
                        meta.error &&
                        formatMessage({ id: meta.error })
                      }
                    />
                  )}
                </Field>
              </FieldItem>
            </Form>
          )}
        </Formik>
        <NotificationsForm
          isLoading={loading}
          errorMessage={errorMessage}
          successMessage={successMessage}
          onChange={onChange}
          preferencesValues={{
            news: workspace.news,
            securityUpdates: workspace.securityUpdates,
          }}
        />
      </Content>
    </SettingsCard>
  );
};
