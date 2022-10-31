import classNames from "classnames";
import { Form, Formik } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";
import * as yup from "yup";

import { Label } from "components";
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

const ValidationSchema = yup.object().shape({
  name: yup.string().required("form.empty.error"),
});

const options = [
  {
    value: "US",
    label: (
      <>
        {/* <US style={{ height: "14px" }} /> */}
        <span style={{ paddingLeft: "10px" }}>United States</span>
      </>
    ),
  },
  { value: "strawberry", label: "Strawberry" },
  { value: "vanilla", label: "Vanilla" },
];

export const DataResidencyView: React.FC = () => {
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
        {({ dirty, isSubmitting, resetForm, isValid }) => (
          <Form>
            <Content>
              <FormattedMessage id="settings.dataResidency.description" />
              <div className={classNames(styles.formItem, styles.inline)}>
                <div>
                  <Label>
                    <FormattedMessage id="settings.dataResidency.form.dropdownLabel" />
                    <InfoTooltip>
                      <FormattedMessage id="settings.dataResidency.form.dropdownLabel.tooltip" />
                    </InfoTooltip>
                  </Label>
                </div>
                <DropDown options={options} />
              </div>
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
