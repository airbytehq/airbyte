import React from "react";

import { ControlLabels } from "components/LabeledControl";

import { FormBaseItem } from "core/form/types";

import { LabelMessage } from "./LabelMessage";

interface LabelMessageProps {
  property: FormBaseItem;
  error: string | undefined;
  touched: boolean;
}

const Label: React.FC<LabelMessageProps> = ({ property, error, touched, children }) => {
  const labelText = property.title || property.fieldKey;
  const labelRequiredAppendix = property.isRequired ? " *" : "";
  const label = `${labelText}${labelRequiredAppendix}`;

  const displayError = !!error && touched;

  return (
    <ControlLabels
      labelAdditionLength={0}
      error={displayError}
      label={label}
      message={<LabelMessage property={property} error={error} touched={touched} />}
    >
      {children}
    </ControlLabels>
  );
};

export { Label };
