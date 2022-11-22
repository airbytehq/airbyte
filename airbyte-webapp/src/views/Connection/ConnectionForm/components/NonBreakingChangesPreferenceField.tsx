import { FieldProps, useField } from "formik";
import { useMemo } from "react";
import { useIntl } from "react-intl";

import { ControlLabels } from "components";
import { DropDown } from "components/ui/DropDown";

import { NonBreakingChangesPreference } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

import styles from "./NonBreakingChangesPreferenceField.module.scss";

export const NonBreakingChangesPreferenceField: React.FC<FieldProps<string>> = ({ field, form }) => {
  const { formatMessage } = useIntl();
  // todo: is the default set when the connection object is created or do i need to set it here...

  const preferenceOptions = useMemo(() => {
    const values = Object.values(NonBreakingChangesPreference);
    return values.map((value) => ({
      value,
      label: formatMessage({ id: `connectionForm.nonBreakingChangesPreference.${value}` }),
      testId: `nonBreakingChangesPreference-${value}`,
    }));
  }, [formatMessage]);

  const { mode } = useConnectionFormService();
  const [, meta] = useField(field.name);

  return (
    <div className={styles.flexRow}>
      <div className={styles.leftFieldCol}>
        <ControlLabels
          className={styles.connectorLabel}
          nextLine
          label={formatMessage({
            id: "connectionForm.nonBreakingChangesPreference.label",
          })}
          message={formatMessage({
            id: "connectionForm.nonBreakingChangesPreference.message",
          })}
        />
      </div>
      <div className={styles.rightFieldCol} style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}>
        <DropDown
          {...field}
          options={preferenceOptions}
          error={!!meta.error && meta.touched}
          data-testid="nonBreakingChangesPreference"
          value={field.value}
          onChange={({ value }) => form.setFieldValue(field.name, value)}
        />
      </div>
    </div>
  );
};
