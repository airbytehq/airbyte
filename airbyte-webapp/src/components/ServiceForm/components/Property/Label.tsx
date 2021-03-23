import React from "react";
import { useField } from "formik";

import { ControlLabels } from "components/LabeledControl";
import { FormBaseItem } from "core/form/types";

import { LabelMessage } from "./LabelMessage";

type LabelMessageProps = {
  property: FormBaseItem;
};

const Label: React.FC<LabelMessageProps> = ({ property, children }) => {
  const [, meta] = useField(property.fieldName);

  const labelText = property.title || property.fieldKey;
  const labelRequiredAppendix = property.isRequired ? " *" : "";
  const label = `${labelText}${labelRequiredAppendix}`;

  const displayError = !!meta.error && meta.touched;

  return (
    <ControlLabels
      labelAdditionLength={0}
      error={displayError}
      label={label}
      message={<LabelMessage property={property} />}
    >
      {children}
    </ControlLabels>
  );
};

export { Label };
