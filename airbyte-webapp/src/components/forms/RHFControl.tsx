import { HTMLInputTypeAttribute } from "react";

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

export const RHFControl: React.FC<RHFControlProps> = ({ fieldType, ...props }) => {
  if (fieldType === "input") {
    return <RHFInputWrapper {...props} />;
  }

  if (fieldType === "date") {
    return <RHFDateWrapper {...props} />;
  }

  throw new Error(`No matching form input found for type: ${fieldType}`);
};
