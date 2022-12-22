import { useField } from "formik";

import GroupControls from "components/GroupControls";
import { ControlLabels } from "components/LabeledControl";
import { CheckBox } from "components/ui/CheckBox";

import styles from "./ToggleGroupField.module.scss";

interface ToggleGroupFieldProps {
  label: string;
  tooltip: string;
  fieldPath: string;
  initialValues: unknown;
}

export const ToggleGroupField: React.FC<React.PropsWithChildren<ToggleGroupFieldProps>> = ({
  children,
  label,
  tooltip,
  fieldPath,
  initialValues,
}) => {
  const [field, , helpers] = useField(fieldPath);
  const enabled = field.value !== undefined;

  const labelComponent = (
    <div className={styles.label}>
      <CheckBox
        checked={enabled}
        onChange={(event) => {
          event.target.checked ? helpers.setValue(initialValues) : helpers.setValue(undefined);
        }}
      />
      <ControlLabels label={label} infoTooltipContent={tooltip} />
    </div>
  );

  return enabled ? <GroupControls label={labelComponent}>{children}</GroupControls> : labelComponent;
};
