import { useField } from "formik";
import { FormattedMessage } from "react-intl";

import { ControlLabels } from "components/LabeledControl";
import { DropDown } from "components/ui/DropDown";
import { Input } from "components/ui/Input";
import { TagInput } from "components/ui/TagInput";
import { Text } from "components/ui/Text";

import styles from "./BuilderField.module.scss";

interface EnumFieldProps {
  options: string[];
  value: string;
  setValue: (value: string) => void;
  error: boolean;
}

interface ArrayFieldProps {
  name: string;
  value: string[];
  setValue: (value: string[]) => void;
  error: boolean;
}

interface BaseFieldProps {
  // path to the location in the Connector Manifest schema which should be set by this component
  path: string;
  label: string;
  tooltip?: string;
  optional?: boolean;
}

type BuilderFieldProps = BaseFieldProps & ({ type: "text" | "array" } | { type: "enum"; options: string[] });

const EnumField: React.FC<EnumFieldProps> = ({ options, value, setValue, error, ...props }) => {
  return (
    <DropDown
      {...props}
      options={options.map((option) => {
        return { label: option, value: option };
      })}
      onChange={(selected) => selected && setValue(selected.value)}
      value={value}
      error={error}
    />
  );
};

const ArrayField: React.FC<ArrayFieldProps> = ({ name, value, setValue, error }) => {
  return <TagInput name={name} fieldValue={value} onChange={(value) => setValue(value)} error={error} />;
};

export const BuilderField: React.FC<BuilderFieldProps> = ({ path, label, tooltip, optional = false, ...props }) => {
  const [field, meta, helpers] = useField(path);
  const hasError = !!meta.error && meta.touched;

  return (
    <ControlLabels className={styles.container} label={label} infoTooltipContent={tooltip} optional={optional}>
      {props.type === "text" && <Input {...field} type={props.type} value={field.value ?? ""} error={hasError} />}
      {props.type === "array" && (
        <ArrayField name={path} value={field.value ?? []} setValue={helpers.setValue} error={hasError} />
      )}
      {props.type === "enum" && (
        <EnumField
          options={props.options}
          value={field.value ?? props.options[0]}
          setValue={helpers.setValue}
          error={hasError}
        />
      )}
      {hasError && (
        <Text className={styles.error}>
          <FormattedMessage id={meta.error} />
        </Text>
      )}
    </ControlLabels>
  );
};
