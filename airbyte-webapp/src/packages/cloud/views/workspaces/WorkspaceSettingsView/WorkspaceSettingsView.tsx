import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Form, Formik, Field, FieldProps } from "formik";

import {
  Content,
  SettingsCard,
} from "pages/SettingsPage/pages/SettingsComponents";
import { Button, LabeledInput, LoadingButton } from "components";
import { useWorkspaceService } from "packages/cloud/services/workspaces/WorkspacesService";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";

const Header = styled.div`
  display: flex;
  justify-content: space-between;
`;

const Buttons = styled.div`
  margin-top: 10px;
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;

  & > button {
    margin-left: 5px;
  }
`;

export const WorkspaceSettingsView: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  const { selectWorkspace, removeWorkspace } = useWorkspaceService();
  const { name, workspaceId } = useCurrentWorkspace();
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
          onSubmit={async (_, formikHelpers) =>
            formikHelpers.setFieldError("name", "Not implemented")
          }
        >
          {({ dirty, isSubmitting, resetForm }) => (
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
                <Buttons>
                  <Button
                    secondary
                    disabled={!dirty}
                    onClick={() => resetForm()}
                  >
                    cancel
                  </Button>
                  <LoadingButton
                    type="submit"
                    disabled={!dirty}
                    isLoading={isSubmitting}
                  >
                    save changes
                  </LoadingButton>
                </Buttons>
              </Content>
            </Form>
          )}
        </Formik>
      </SettingsCard>
      <SettingsCard
        title={
          <Header>
            <FormattedMessage id="settings.generalSettings.deleteLabel" />
            <LoadingButton
              isLoading={removeWorkspace.isLoading}
              danger
              onClick={() => removeWorkspace.mutateAsync(workspaceId)}
            >
              <FormattedMessage id="settings.generalSettings.deleteText" />
            </LoadingButton>
          </Header>
        }
      />
    </>
  );
};
