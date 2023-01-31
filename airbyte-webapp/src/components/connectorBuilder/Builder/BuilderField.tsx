import { FastField, FastFieldProps, FieldInputProps } from "formik";
import { ReactNode } from "react";
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
  tooltip?: React.ReactNode;
  readOnly?: boolean;
  optional?: boolean;
  pattern?: RegExp;
  adornment?: ReactNode;
  className?: string;
}

export type BuilderFieldProps = BaseFieldProps &
  (
    | { type: "string" | "number" | "integer"; onChange?: (newValue: string) => void; onBlur?: (value: string) => void }
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

const InnerBuilderField: React.FC<BuilderFieldProps & FastFieldProps<unknown>> = ({
  path,
  label,
  tooltip,
  optional = false,
  readOnly,
  pattern,
  field,
  meta,
  form,
  adornment,
  ...props
}) => {
  const hasError = !!meta.error && meta.touched;

  if (props.type === "boolean") {
    return (
      <LabeledSwitch
        {...(field as FieldInputProps<string>)}
        checked={field.value as boolean}
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
    form.setFieldValue(path, newValue);
  };

  return (
    <ControlLabels className={styles.container} label={label} infoTooltipContent={tooltip} optional={optional}>
      {(props.type === "number" || props.type === "string" || props.type === "integer") && (
        <Input
          {...field}
          onChange={(e) => {
            field.onChange(e);
            if (e.target.value === "") {
              form.setFieldValue(path, undefined);
            }
            props.onChange?.(e.target.value);
          }}
          className={props.className}
          type={props.type}
          value={(field.value as string | number | undefined) ?? ""}
          error={hasError}
          readOnly={readOnly}
          adornment={adornment}
          onBlur={(e) => {
            props.onBlur?.(e.target.value);
          }}
        />
      )}
      {props.type === "array" && (
        <ArrayField
          name={path}
          value={(field.value as string[] | undefined) ?? []}
          setValue={setValue}
          error={hasError}
        />
      )}
      {props.type === "enum" && (
        <EnumField
          options={props.options}
          value={field.value as string}
          setValue={setValue}
          error={hasError}
          data-testid={path}
        />
      )}
      {hasError && (
        <Text className={styles.error}>
          <FormattedMessage
            id={meta.error}
            values={meta.error === "form.pattern.error" && pattern ? { pattern: String(pattern) } : undefined}
          />
        </Text>
      )}
    </ControlLabels>
  );
};

export const BuilderField: React.FC<BuilderFieldProps> = (props) => {
  return (
    // The key is set to enforce a re-render of the component if the type change, otherwise changes in props might not be reflected correctly
    <FastField name={props.path} key={props.type}>
      {({ field, form, meta }: FastFieldProps<unknown>) => (
        <InnerBuilderField {...props} field={field} form={form} meta={meta} />
      )}
    </FastField>
  );
};
