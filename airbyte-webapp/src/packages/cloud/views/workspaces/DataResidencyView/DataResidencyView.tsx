import classNames from "classnames";
import { US } from "country-flag-icons/react/3x2";
import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { Label, LabeledInput, LabeledSwitch } from "components";
import { Button } from "components/ui/Button";
import { DropDown } from "components/ui/DropDown";
import { InfoTooltip } from "components/ui/Tooltip";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useUpdateCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { Content, SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";
import { useInvalidateWorkspace } from "services/workspaces/WorkspacesService";

import styles from "./DataResidencyView.module.scss";

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

const options = [
  {
    value: "US",
    label: (
      <>
        <US style={{ height: "10px" }} />
        <span style={{ paddingLeft: "10px" }}>United States</span>
      </>
    ),
  },
  { value: "strawberry", label: "Strawberry" },
  { value: "vanilla", label: "Vanilla" },
];

export const DataResidencyView: React.FC = () => {
  const { formatMessage } = useIntl();
  useTrackPage(PageTrackingCodes.SETTINGS_WORKSPACE);
  const workspace = useCurrentWorkspace();
  const { mutateAsync: updateCloudWorkspace } = useUpdateCloudWorkspace();
  const invalidateWorkspace = useInvalidateWorkspace(workspace.workspaceId);
  const [isAdvancedMode, setAdvancedMode] = useAdvancedModeSetting();

  return (
    <SettingsCard
      title={
        <div className={styles.header}>
          <FormattedMessage id="settings.dataResidency" />
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
                <FormattedMessage id="settings.dataResidency.description" />
              </Label>
              <DropDown options={options} />
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
  );
};
