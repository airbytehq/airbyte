import classNames from "classnames";
import { HTMLInputTypeAttribute } from "react";
import { Path, useFormContext } from "react-hook-form";

import { Text } from "components/ui/Text";

import styles from "./RHFControl.module.scss";
import { RHFDateWrapper } from "./RHFDateWrapper";
import { FormValues } from "./RHFForm";
import { RHFInputWrapper } from "./RHFInputWrapper";

type RHFControlProps<T> = RHFInputFieldProps<T> | RHFDatePickerProps<T>;

interface RHFControlBaseProps<T extends FormValues> {
  /**
   * fieldType determines what form element is rendered. Depending on the chosen fieldType, additional props may be optional or required.
   */
  fieldType: "input" | "date";
  /**
   * The field name must match any provided default value or validation schema.
   */
  name: Path<T>;
  /**
   * A label that is displayed above the form control
   */
  label: string;
  /**
   * An optional description that appears under the label
   */
  description?: string;
}

/**
 * These properties are only relevant at the control level. They can therefore be omitted before passing along to the underlying form input.
 */
export type OmittableProperties = "fieldType" | "label" | "description";

export interface RHFInputFieldProps<T> extends RHFControlBaseProps<T> {
  fieldType: "input";
  type?: HTMLInputTypeAttribute;
  hasError?: boolean;
}

export interface RHFDatePickerProps<T> extends RHFControlBaseProps<T> {
  fieldType: "date";
  /**
   * The desired format for the date string:
   * - **date**       *YYYY-MM-DD* (default)
   * - **date-time**  *YYYY-MM-DDTHH:mm:ssZ*
   */
  format?: "date" | "date-time";
  hasError?: boolean;
}

export const RHFControl = <T extends FormValues>({
  fieldType,
  label,
  description,
  name,
  ...props
}: RHFControlProps<T>) => {
  const { formState, getFieldState } = useFormContext<T>();
  const { error, isTouched } = getFieldState(name, formState); // It is subscribed now and reactive to error state updated
  const showError = error && isTouched;

  // Properties to pass to the underlying input
  const inputProps = {
    ...props,
    hasError: showError,
  };

  function renderControl() {
    if (fieldType === "input") {
      return <RHFInputWrapper name={name} {...inputProps} />;
    }

    if (fieldType === "date") {
      return <RHFDateWrapper name={name} {...inputProps} />;
    }

    throw new Error(`No matching form input found for type: ${fieldType}`);
  }

  return (
    <div className={styles.control}>
      <label>
        <div className={classNames(styles.label)}>
          <Text size="lg">{label}</Text>
          {description && <Text className={styles.description}>{description}</Text>}
        </div>
        {renderControl()}
      </label>
      {error && (
        <p className={classNames(styles.errorMessage, { [styles["errorMessage--visible"]]: showError })}>
          {error.message}
        </p>
      )}
    </div>
  );
};
