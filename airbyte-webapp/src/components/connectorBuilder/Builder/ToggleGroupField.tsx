import { useField } from "formik";

import GroupControls from "components/GroupControls";
import { ControlLabels } from "components/LabeledControl";
import { CheckBox } from "components/ui/CheckBox";

import styles from "./ToggleGroupField.module.scss";

interface ToggleGroupFieldProps<T> {
  label: string;
  tooltip: string;
  fieldPath: string;
  initialValues: T;
}

// eslint-disable-next-line react/function-component-definition
export function ToggleGroupField<T>({
  children,
  label,
  tooltip,
  fieldPath,
  initialValues,
}: React.PropsWithChildren<ToggleGroupFieldProps<T>>) {
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
}
