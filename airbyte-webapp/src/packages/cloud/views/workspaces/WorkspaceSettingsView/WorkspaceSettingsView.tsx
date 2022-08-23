import classNames from "classnames";
import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Button, LabeledInput, LabeledSwitch, LoadingButton } from "components";

import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import {
  useRemoveWorkspace,
  useUpdateWorkspace,
  useWorkspaceService,
} from "packages/cloud/services/workspaces/WorkspacesService";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

import styles from "./WorkspaceSettingsView.module.scss";

export const WorkspaceSettingsView: React.FC = () => {
  const { formatMessage } = useIntl();

  const { exitWorkspace } = useWorkspaceService();
  const workspace = useCurrentWorkspace();
  const removeWorkspace = useRemoveWorkspace();
  const updateWorkspace = useUpdateWorkspace();
  const [isAdvancedMode, setAdvancedMode] = useAdvancedModeSetting();

  return (
    <>
      <SettingsCard
        title={
          <div className={styles.header}>
            <FormattedMessage id="settings.generalSettings" />
            <Button type="button" onClick={exitWorkspace} data-testid="button.changeWorkspace">
              <FormattedMessage id="settings.generalSettings.changeWorkspace" />
            </Button>
          </div>
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
                <LabeledSwitch
                  label="Advanced Mode"
                  checked={isAdvancedMode}
                  onChange={(ev) => setAdvancedMode(ev.target.checked)}
                  className={styles.formItem}
                />
                <div className={classNames(styles.formItem, styles.buttonGroup)}>
                  <Button type="button" secondary disabled={!dirty} onClick={() => resetForm()}>
                    cancel
                  </Button>
                  <LoadingButton type="submit" disabled={!isValid} isLoading={isSubmitting}>
                    save changes
                  </LoadingButton>
                </div>
              </Content>
            </Form>
          )}
        </Formik>
      </SettingsCard>
      <SettingsCard
        title={
          <div className={styles.header}>
            <FormattedMessage id="settings.generalSettings.deleteLabel" />
            <LoadingButton
              isLoading={removeWorkspace.isLoading}
              danger
              onClick={() => removeWorkspace.mutateAsync(workspace.workspaceId)}
            >
              <FormattedMessage id="settings.generalSettings.deleteText" />
            </LoadingButton>
          </div>
        }
      />
    </>
  );
};
