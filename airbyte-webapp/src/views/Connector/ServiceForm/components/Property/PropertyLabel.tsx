import React from "react";
import { FormattedMessage } from "react-intl";

import { ControlLabels } from "components/LabeledControl";

import { FormBlock } from "core/form/types";

import { LabelInfo } from "./LabelInfo";

interface PropertyLabelProps {
  property: FormBlock;
  error?: string;
  touched?: boolean;
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

  const errorValues =
    error === "form.pattern.error" && property._type === "formItem" ? { pattern: property.pattern } : undefined;
  const errorMessage = <FormattedMessage id={error} values={errorValues} />;

  const examples = property._type === "formItem" || property._type === "formGroup" ? property.examples : undefined;

  return (
    <ControlLabels
      className={className}
      labelAdditionLength={0}
      label={label}
      infoMessage={<LabelInfo label={label} examples={examples} description={property.description} />}
      errorMessage={displayError ? errorMessage : undefined}
      optional={optional !== undefined ? optional : !property.isRequired}
    >
      {children}
    </ControlLabels>
  );
};

export { PropertyLabel };
