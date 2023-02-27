import classNames from "classnames";
import { HTMLInputTypeAttribute, ReactNode } from "react";
import { FieldError, Path, useFormContext } from "react-hook-form";

import { OptionType } from "components/ui/DropDown";
import { Text } from "components/ui/Text";
import { InfoTooltip } from "components/ui/Tooltip";

import styles from "./RHFControl.module.scss";
import { RHFDateWrapper } from "./RHFDateWrapper";
import { RHFDropDownWrapper } from "./RHFDropDownWrapper";
import { FormValues } from "./RHFForm";
import { RHFInputWrapper } from "./RHFInputWrapper";

type RHFControlProps<T> = RHFDropDownProps<T> | RHFInputFieldProps<T> | RHFDatePickerProps<T>;

interface RHFControlBaseProps<T extends FormValues> {
  /**
   * fieldType determines what form element is rendered. Depending on the chosen fieldType, additional props may be optional or required.
   */
  fieldType: "input" | "date" | "dropdown";
  /**
   * The field name must match any provided default value or validation schema.
   */
  name: Path<T>;
  /**
   * A label that is displayed above the form control
   */
  label: string;
  /**
   * A tooltip that appears next to the form label
   */
  labelTooltip?: ReactNode;
  /**
   * An optional description that appears under the label
   */
  description?: string;
  hasError?: boolean;
}

/**
 * These properties are only relevant at the control level. They can therefore be omitted before passing along to the underlying form input.
 */
export type OmittableProperties = "fieldType" | "label" | "labelTooltip" | "description";

export interface RHFInputFieldProps<T> extends RHFControlBaseProps<T> {
  fieldType: "input";
  type?: HTMLInputTypeAttribute;
}

export interface RHFDatePickerProps<T> extends RHFControlBaseProps<T> {
  fieldType: "date";
  /**
   * The desired format for the date string:
   * - **date**       *YYYY-MM-DD* (default)
   * - **date-time**  *YYYY-MM-DDTHH:mm:ssZ*
   */
  format?: "date" | "date-time";
}

export interface RHFDropDownProps<T> extends RHFControlBaseProps<T> {
  fieldType: "dropdown";
  options: OptionType[];
}

export const RHFControl = <T extends FormValues>({
  label,
  labelTooltip,
  description,
  ...props
}: RHFControlProps<T>) => {
  const { formState, getFieldState } = useFormContext<T>();
  const { error } = getFieldState(props.name, formState); // It is subscribed now and reactive to error state updated

  // Properties to pass to the underlying input
  const inputProps = {
    ...props,
    hasError: Boolean(error),
  };

  function renderControl() {
    if (inputProps.fieldType === "input") {
      return <RHFInputWrapper {...inputProps} />;
    }

    if (inputProps.fieldType === "date") {
      return <RHFDateWrapper {...inputProps} />;
    }

    if (inputProps.fieldType === "dropdown") {
      return <RHFDropDownWrapper {...inputProps} />;
    }

    throw new Error(`No matching form input found for type: ${props.fieldType}`);
  }

  return (
    <div className={styles.control}>
      <label>
        <RHFFormLabel description={description} label={label} labelTooltip={labelTooltip} />
        {renderControl()}
      </label>
      {error && <RHFControlError error={error} />}
    </div>
  );
};

interface RHFFormLabelProps {
  description?: string;
  label: string;
  labelTooltip?: ReactNode;
}

export const RHFFormLabel: React.FC<RHFFormLabelProps> = ({ description, label, labelTooltip }) => {
  return (
    <div className={classNames(styles.label)}>
      <Text size="lg">
        {label}
        {labelTooltip && <InfoTooltip placement="top-start">{labelTooltip}</InfoTooltip>}
      </Text>
      {description && <Text className={styles.description}>{description}</Text>}
    </div>
  );
};

interface RHFControlErrorProps {
  error: FieldError;
}

export const RHFControlError: React.FC<RHFControlErrorProps> = ({ error }) => {
  return (
    <p className={classNames(styles.errorMessage, { [styles["errorMessage--visible"]]: true })}>{error.message}</p>
  );
};
