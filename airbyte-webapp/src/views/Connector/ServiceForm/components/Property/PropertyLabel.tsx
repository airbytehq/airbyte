import React from "react";

import { ControlLabels } from "components/LabeledControl";

import { FormBlock } from "core/form/types";

import { LabelInfo } from "./LabelInfo";

interface PropertyLabelProps {
  property: FormBlock;
  label: React.ReactNode;
  description?: string;
  optional?: boolean;
  className?: string;
}

const PropertyLabel: React.FC<PropertyLabelProps> = ({
  property,
  label,
  description,
  optional,
  className,
  children,
}) => {
  const examples = property._type === "formItem" || property._type === "formGroup" ? property.examples : undefined;

  return (
    <ControlLabels
      className={className}
      labelAdditionLength={0}
      label={label}
      infoMessage={<LabelInfo label={label} examples={examples} description={description ?? property.description} />}
      optional={optional ?? !property.isRequired}
    >
      {children}
    </ControlLabels>
  );
};

export { PropertyLabel };
