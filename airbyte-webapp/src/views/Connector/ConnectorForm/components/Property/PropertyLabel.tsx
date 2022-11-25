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
  htmlFor?: string;
}

export const PropertyLabel: React.FC<React.PropsWithChildren<PropertyLabelProps>> = ({
  property,
  label,
  description,
  optional,
  className,
  children,
  htmlFor,
}) => {
  const examples = property._type === "formItem" || property._type === "formGroup" ? property.examples : undefined;
  const descriptionToDisplay = description ?? property.description;

  return (
    <ControlLabels
      className={className}
      label={label}
      infoTooltipContent={
        (descriptionToDisplay || examples) && (
          <LabelInfo label={label} description={descriptionToDisplay} examples={examples} />
        )
      }
      optional={optional ?? !property.isRequired}
      htmlFor={htmlFor}
    >
      {children}
    </ControlLabels>
  );
};
