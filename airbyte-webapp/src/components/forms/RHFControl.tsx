import classNames from "classnames";
import { HTMLInputTypeAttribute } from "react";
import { useFormContext } from "react-hook-form";

import { Text } from "components/ui/Text";

import styles from "./RHFControl.module.scss";
import { RHFDateWrapper } from "./RHFDateWrapper";
import { RHFInputWrapper } from "./RHFInputWrapper";

type RHFControlProps = RHFInputFieldProps | RHFDatePickerProps;

interface RHFControlBaseProps {
  /**
   * fieldType determines what form element is rendered. Depending on the chosen fieldType, additional props may be optional or required.
   */
  fieldType: "input" | "date";
  /**
   * The field name must match any provided default value or validation schema.
   */
  name: string;
  /**
   * A label that is displayed above the form control
   */
  label: string;
  /**
   * An optional description that appears under the label
   */
  description?: string;
}

export type OmittableProperties = "fieldType" | "label" | "description";

export interface RHFInputFieldProps extends RHFControlBaseProps {
  fieldType: "input";
  type?: HTMLInputTypeAttribute;
  hasError?: boolean;
}

export interface RHFDatePickerProps extends RHFControlBaseProps {
  fieldType: "date";
  /**
   * The desired format for the date string:
   * - **date**       *YYYY-MM-DD* (default)
   * - **date-time**  *YYYY-MM-DDTHH:mm:ssZ*
   */
  format?: "date" | "date-time";
}

export const RHFControl: React.FC<RHFControlProps> = ({ fieldType, label, description, name, ...props }) => {
  const { formState, getFieldState } = useFormContext();
  const { error, isTouched } = getFieldState(name, formState); // It is subscribed now and reactive to error state updated
  const showError = error && isTouched;

  function renderControl() {
    if (fieldType === "input") {
      return <RHFInputWrapper name={name} hasError={showError} {...props} />;
    }

    if (fieldType === "date") {
      return <RHFDateWrapper name={name} {...props} />;
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
