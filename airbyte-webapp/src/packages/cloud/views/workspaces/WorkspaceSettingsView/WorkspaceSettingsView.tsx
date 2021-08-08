import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Form, Formik, Field, FieldProps } from "formik";

import {
  Content,
  SettingsCard,
} from "pages/SettingsPage/pages/SettingsComponents";
import { Button, LabeledInput } from "components";
import { useWorkspaceService } from "packages/cloud/services/workspaces/WorkspacesService";
import { useCurrentWorkspace } from "components/hooks/services/useWorkspace";

const Header = styled.div`
  display: flex;
  justify-content: space-between;
`;

export const WorkspaceSettingsView: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  const { selectWorkspace } = useWorkspaceService();
  const { name } = useCurrentWorkspace();
  return (
    <>
      <SettingsCard
        title={
          <Header>
            <FormattedMessage id="settings.generalSettings" />
            <Button onClick={() => selectWorkspace("")}>
              <FormattedMessage id="settings.generalSettings.changeWorkspace" />
            </Button>
          </Header>
        }
      >
        <Formik
          initialValues={{ name: name }}
          onSubmit={(_, formikHelpers) =>
            formikHelpers.setFieldError("name", "Not implemeneted")
          }
        >
          {() => (
            <Form>
              <Content>
                <Field name="name">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={
                        <FormattedMessage id="settings.generalSettings.form.name.label" />
                      }
                      placeholder={formatMessage({
                        id: "settings.generalSettings.form.name.placeholder",
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
              </Content>
            </Form>
          )}
        </Formik>
      </SettingsCard>
      <SettingsCard
        title={
          <Header>
            <FormattedMessage id="settings.generalSettings.deleteLabel" />
            <Button danger>
              <FormattedMessage id="settings.generalSettings.deleteText" />
            </Button>
          </Header>
        }
      />
    </>
  );
};
