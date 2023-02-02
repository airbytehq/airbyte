import { HTMLInputTypeAttribute } from "react";
import { useFormContext } from "react-hook-form";

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
}

export interface RHFInputFieldProps extends RHFControlBaseProps {
  fieldType: "input";
  type?: HTMLInputTypeAttribute;
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

export const RHFControl: React.FC<RHFControlProps> = ({ fieldType, name, ...props }) => {
  const { formState, getFieldState } = useFormContext();
  const { error, isTouched } = getFieldState(name, formState); // It is subscribed now and reactive to error state updated

  function renderControl() {
    if (fieldType === "input") {
      return <RHFInputWrapper name={name} {...props} />;
    }

    if (fieldType === "date") {
      return <RHFDateWrapper name={name} {...props} />;
    }

    throw new Error(`No matching form input found for type: ${fieldType}`);
  }

  return (
    <div>
      {renderControl()}
      {error && isTouched && <p>{error}</p>}
    </div>
  );
};
