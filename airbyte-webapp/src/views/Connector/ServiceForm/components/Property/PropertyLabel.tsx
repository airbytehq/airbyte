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
  const examples =
    // Show examples for individual items and groups, unless its a date field, since we don't
    // want to confuse the user around potential date format examples
    (property._type === "formItem" && property.format !== "date-time" && property.format !== "date") ||
    property._type === "formGroup"
      ? property.examples
      : undefined;
  const descriptionToDisplay = description ?? property.description;

  return (
    <ControlLabels
      className={className}
      labelAdditionLength={0}
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
