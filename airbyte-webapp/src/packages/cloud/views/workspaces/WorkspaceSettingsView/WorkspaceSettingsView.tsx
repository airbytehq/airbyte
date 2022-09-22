import classNames from "classnames";
import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { Button, Label, LabeledInput, LabeledSwitch, LoadingButton } from "components";
import { InfoTooltip } from "components/base/Tooltip";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import {
  useRemoveCloudWorkspace,
  useUpdateCloudWorkspace,
} from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";
import { useInvalidateWorkspace, useWorkspaceService } from "services/workspaces/WorkspacesService";

import styles from "./WorkspaceSettingsView.module.scss";

const AdvancedModeSwitchLabel = () => (
  <>
    <FormattedMessage id="settings.generalSettings.form.advancedMode.switchLabel" />
    <InfoTooltip>
      <FormattedMessage id="settings.generalSettings.form.advancedMode.tooltip" />
    </InfoTooltip>
  </>
);

const ValidationSchema = yup.object().shape({
  name: yup.string().required("form.empty.error"),
});

export const WorkspaceSettingsView: React.FC = () => {
  const { formatMessage } = useIntl();
  useTrackPage(PageTrackingCodes.SETTINGS_WORKSPACE);
  const { exitWorkspace } = useWorkspaceService();
  const workspace = useCurrentWorkspace();
  const { mutateAsync: removeCloudWorkspace, isLoading: isRemovingCloudWorkspace } = useRemoveCloudWorkspace();
  const { mutateAsync: updateCloudWorkspace } = useUpdateCloudWorkspace();
  const invalidateWorkspace = useInvalidateWorkspace(workspace.workspaceId);
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
          initialValues={{
            name: workspace.name,
            advancedMode: isAdvancedMode,
          }}
          onSubmit={async (payload) => {
            const { workspaceId } = workspace;
            setAdvancedMode(payload.advancedMode);
            await updateCloudWorkspace({
              workspaceId,
              name: payload.name,
            });
            await invalidateWorkspace();
          }}
          enableReinitialize
          validationSchema={ValidationSchema}
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
                  <Button type="button" secondary disabled={!dirty} onClick={() => resetForm()}>
                    <FormattedMessage id="form.cancel" />
                  </Button>
                  <LoadingButton type="submit" disabled={!dirty || !isValid} isLoading={isSubmitting}>
                    <FormattedMessage id="form.saveChanges" />
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
              isLoading={isRemovingCloudWorkspace}
              danger
              onClick={() => removeCloudWorkspace(workspace.workspaceId)}
            >
              <FormattedMessage id="settings.generalSettings.deleteText" />
            </LoadingButton>
          </div>
        }
      />
    </>
  );
};
