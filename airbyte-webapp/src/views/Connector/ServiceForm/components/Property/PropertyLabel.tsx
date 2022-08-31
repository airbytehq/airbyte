import React from "react";
import { FormattedMessage } from "react-intl";

import { ControlLabels } from "components/LabeledControl";

import { FormBaseItem } from "core/form/types";

import { LabelInfo } from "./LabelInfo";

interface LabelMessageProps {
  property: FormBaseItem;
  error: string | undefined;
  touched: boolean;
  label: React.ReactNode;
}

const PropertyLabel: React.FC<LabelMessageProps> = ({ property, label, error, touched, children }) => {
  const displayError = !!error && touched;

  const errorValues = error === "form.pattern.error" ? { pattern: property.pattern } : undefined;
  const errorMessage = <FormattedMessage id={error} values={errorValues} />;

  return (
    <ControlLabels
      labelAdditionLength={0}
      label={label}
      infoMessage={<LabelInfo property={property} error={error} touched={touched} />}
      errorMessage={displayError ? errorMessage : undefined}
      required={property.isRequired}
    >
      {children}
    </ControlLabels>
  );
};

export { PropertyLabel };
