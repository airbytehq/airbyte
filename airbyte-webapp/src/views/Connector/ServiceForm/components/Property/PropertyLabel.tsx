import React from "react";
import { FormattedMessage } from "react-intl";

import { ControlLabels } from "components/LabeledControl";

import { FormBaseItem } from "core/form/types";

import { LabelInfo } from "./LabelInfo";

interface PropertyLabelProps {
  property: FormBaseItem;
  error: string | undefined;
  touched: boolean;
  label: React.ReactNode;
  optional?: boolean;
  className?: string;
}

const PropertyLabel: React.FC<PropertyLabelProps> = ({
  property,
  label,
  error,
  touched,
  optional,
  className,
  children,
}) => {
  const displayError = !!error && touched;

  const errorValues = error === "form.pattern.error" ? { pattern: property.pattern } : undefined;
  const errorMessage = <FormattedMessage id={error} values={errorValues} />;

  return (
    <ControlLabels
      className={className}
      labelAdditionLength={0}
      label={label}
      infoMessage={<LabelInfo property={property} label={label} />}
      errorMessage={displayError ? errorMessage : undefined}
      optional={optional !== undefined ? optional : !property.isRequired}
    >
      {children}
    </ControlLabels>
  );
};

export { PropertyLabel };
