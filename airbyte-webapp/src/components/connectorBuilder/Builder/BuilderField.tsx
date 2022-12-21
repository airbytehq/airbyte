import { useField } from "formik";
import { FormattedMessage } from "react-intl";

import { ControlLabels } from "components/LabeledControl";
import { LabeledSwitch } from "components/LabeledSwitch";
import { DropDown } from "components/ui/DropDown";
import { Input } from "components/ui/Input";
import { TagInput } from "components/ui/TagInput";
import { Text } from "components/ui/Text";
import { InfoTooltip } from "components/ui/Tooltip/InfoTooltip";

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
  readOnly?: boolean;
  optional?: boolean;
}

type BuilderFieldProps = BaseFieldProps &
  (
    | { type: "string" | "number" | "integer"; onChange?: (newValue: string) => void }
    | { type: "boolean"; onChange?: (newValue: boolean) => void }
    | { type: "array"; onChange?: (newValue: string[]) => void }
    | { type: "enum"; onChange?: (newValue: string) => void; options: string[] }
  );

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

export const BuilderField: React.FC<BuilderFieldProps> = ({
  path,
  label,
  tooltip,
  optional = false,
  readOnly,
  ...props
}) => {
  const [field, meta, helpers] = useField(path);
  const hasError = !!meta.error && meta.touched;

  if (props.type === "boolean") {
    return (
      <LabeledSwitch
        {...field}
        checked={field.value}
        label={
          <>
            {label} {tooltip && <InfoTooltip placement="top-start">{tooltip}</InfoTooltip>}
          </>
        }
      />
    );
  }

  const setValue = (newValue: unknown) => {
    props.onChange?.(newValue as string & string[]);
    helpers.setValue(newValue);
  };

  return (
    <ControlLabels className={styles.container} label={label} infoTooltipContent={tooltip} optional={optional}>
      {(props.type === "number" || props.type === "string" || props.type === "integer") && (
        <Input
          {...field}
          onChange={(e) => {
            field.onChange(e);
            props.onChange?.(e.target.value);
          }}
          type={props.type}
          value={field.value ?? ""}
          error={hasError}
          readOnly={readOnly}
        />
      )}
      {props.type === "array" && (
        <ArrayField name={path} value={field.value ?? []} setValue={setValue} error={hasError} />
      )}
      {props.type === "enum" && (
        <EnumField options={props.options} value={field.value} setValue={setValue} error={hasError} />
      )}
      {hasError && (
        <Text className={styles.error}>
          <FormattedMessage id={meta.error} />
        </Text>
      )}
    </ControlLabels>
  );
};
