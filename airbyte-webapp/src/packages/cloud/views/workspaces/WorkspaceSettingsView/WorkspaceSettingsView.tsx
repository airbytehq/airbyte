import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { Button, LabeledInput, LoadingButton } from "components";

import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import {
  useRemoveWorkspace,
  useUpdateWorkspace,
  useWorkspaceService,
} from "packages/cloud/services/workspaces/WorkspacesService";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

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
  const { formatMessage } = useIntl();

  const { exitWorkspace } = useWorkspaceService();
  const workspace = useCurrentWorkspace();
  const removeWorkspace = useRemoveWorkspace();
  const updateWorkspace = useUpdateWorkspace();

  return (
    <>
      <SettingsCard
        title={
          <Header>
            <FormattedMessage id="settings.generalSettings" />
            <Button type="button" onClick={exitWorkspace} data-testid="button.changeWorkspace">
              <FormattedMessage id="settings.generalSettings.changeWorkspace" />
            </Button>
          </Header>
        }
      >
        <Formik
          initialValues={{ name: workspace.name }}
          onSubmit={async (payload) =>
            updateWorkspace.mutateAsync({
              workspaceId: workspace.workspaceId,
              name: payload.name,
            })
          }
        >
          {({ dirty, isSubmitting, resetForm, isValid }) => (
            <Form>
              <Content>
                <Field name="name">
                  {({ field, meta }: FieldProps<string>) => (
                    <LabeledInput
                      {...field}
                      label={<FormattedMessage id="settings.generalSettings.form.name.label" />}
                      placeholder={formatMessage({
                        id: "settings.generalSettings.form.name.placeholder",
                      })}
                      type="text"
                      error={!!meta.error && meta.touched}
                      message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                    />
                  )}
                </Field>
                <Buttons>
                  <Button type="button" secondary disabled={!dirty} onClick={() => resetForm()}>
                    cancel
                  </Button>
                  <LoadingButton type="submit" disabled={!isValid} isLoading={isSubmitting}>
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
              onClick={() => removeWorkspace.mutateAsync(workspace.workspaceId)}
            >
              <FormattedMessage id="settings.generalSettings.deleteText" />
            </LoadingButton>
          </Header>
        }
      />
    </>
  );
};
