import { useField } from "formik";

import { ControlLabels } from "components/LabeledControl";
import { Input } from "components/ui/Input";

interface BuilderFieldProps {
  type: "text" | "number";
  // path to the location in the Connector Manifest schema which should be set by this component
  path: string;
  label: string;
  tooltip?: string;
  optional?: boolean;
}

export const BuilderField: React.FC<BuilderFieldProps> = ({ type, path, label, tooltip, optional = false }) => {
  const [field, meta] = useField(path);
  return (
    <ControlLabels label={label} infoTooltipContent={tooltip} optional={optional}>
      <Input {...field} type={type} value={field.value ?? ""} error={!!meta.error && meta.touched} />
    </ControlLabels>
  );
};
