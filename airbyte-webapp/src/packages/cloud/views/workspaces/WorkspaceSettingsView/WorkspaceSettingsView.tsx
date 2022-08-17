import classNames from "classnames";
import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Button, ButtonType, LabeledInput, Label, LabeledSwitch } from "components";
import { InfoTooltip } from "components/base/Tooltip";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import {
  useRemoveWorkspace,
  useUpdateWorkspace,
  useWorkspaceService,
} from "packages/cloud/services/workspaces/WorkspacesService";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";

import styles from "./WorkspaceSettingsView.module.scss";

const AdvancedModeSwitchLabel = () => (
  <>
    <FormattedMessage id="settings.generalSettings.form.advancedMode.switchLabel" />
    <InfoTooltip>
      <FormattedMessage id="settings.generalSettings.form.advancedMode.tooltip" />
    </InfoTooltip>
  </>
);

export const WorkspaceSettingsView: React.FC = () => {
  const { formatMessage } = useIntl();
  useTrackPage(PageTrackingCodes.SETTINGS_WORKSPACE);
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
            <Button
              type="button"
              onClick={exitWorkspace}
              data-testid="button.changeWorkspace"
              label={<FormattedMessage id="settings.generalSettings.changeWorkspace" />}
            />
          </div>
        }
      >
        <Formik
          initialValues={{
            name: workspace.name,
            advancedMode: isAdvancedMode,
          }}
          onSubmit={async (payload) => {
            setAdvancedMode(payload.advancedMode);
            return updateWorkspace.mutateAsync({
              workspaceId: workspace.workspaceId,
              name: payload.name,
            });
          }}
        >
          {({ dirty, isSubmitting, resetForm, isValid, setFieldValue }) => (
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
                <Label className={styles.formItem}>
                  <FormattedMessage id="settings.generalSettings.form.advancedMode.label" />
                </Label>
                <Field name="advancedMode">
                  {({ field }: FieldProps<boolean>) => (
                    <LabeledSwitch
                      label={<AdvancedModeSwitchLabel />}
                      checked={field.value}
                      onChange={() => setFieldValue(field.name, !field.value)}
                    />
                  )}
                </Field>

                <div className={classNames(styles.formItem, styles.buttonGroup)}>
                  <Button
                    type="button"
                    buttonType={ButtonType.Secondary}
                    disabled={!dirty}
                    onClick={() => resetForm()}
                    label="cancel"
                  />
                  <Button type="submit" disabled={!isValid} isLoading={isSubmitting} label="save changes" />
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
            <Button
              isLoading={removeWorkspace.isLoading}
              buttonType={ButtonType.Danger}
              onClick={() => removeWorkspace.mutateAsync(workspace.workspaceId)}
              label={<FormattedMessage id="settings.generalSettings.deleteText" />}
            />
          </div>
        }
      />
    </>
  );
};
