import classNames from "classnames";
import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { LabeledInput } from "components";
import { Button } from "components/ui/Button";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import {
  useRemoveCloudWorkspace,
  useUpdateCloudWorkspace,
} from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";
import { useInvalidateWorkspace, useWorkspaceService } from "services/workspaces/WorkspacesService";

import styles from "./WorkspaceSettingsView.module.scss";

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
          }}
          onSubmit={async (payload) => {
            const { workspaceId } = workspace;
            await updateCloudWorkspace({
              workspaceId,
              name: payload.name,
            });
            await invalidateWorkspace();
          }}
          enableReinitialize
          validationSchema={ValidationSchema}
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

                <div className={classNames(styles.formItem, styles.buttonGroup)}>
                  <Button type="button" variant="secondary" disabled={!dirty} onClick={() => resetForm()}>
                    <FormattedMessage id="form.cancel" />
                  </Button>
                  <Button type="submit" disabled={!dirty || !isValid} isLoading={isSubmitting}>
                    <FormattedMessage id="form.saveChanges" />
                  </Button>
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
              isLoading={isRemovingCloudWorkspace}
              variant="danger"
              onClick={() => removeCloudWorkspace(workspace.workspaceId)}
            >
              <FormattedMessage id="settings.generalSettings.deleteText" />
            </Button>
          </div>
        }
      />
    </>
  );
};
