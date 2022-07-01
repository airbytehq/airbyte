import { useField } from "formik";
import React from "react";

import { LabeledSwitch, TextWithHTML } from "components";

import { FormBaseItem } from "core/form/types";

import { useServiceForm } from "../../serviceFormContext";
import { Control } from "../Property/Control";
import { Label } from "../Property/Label";

interface PropertySectionProps {
  property: FormBaseItem;
  path?: string;
  disabled?: boolean;
}

const PropertySection: React.FC<PropertySectionProps> = ({ property, path, disabled }) => {
  const propertyPath = path ?? property.path;
  const formikBag = useField(propertyPath);
  const [field, meta] = formikBag;
  const { addUnfinishedFlow, removeUnfinishedFlow, unfinishedFlows, widgetsInfo } = useServiceForm();

  const overriddenComponent = widgetsInfo[propertyPath]?.component;
  if (overriddenComponent) {
    return <>{overriddenComponent(property, { disabled })}</>;
  }

  if (property.type === "boolean") {
    return (
      <LabeledSwitch
        {...field}
        label={property.title || property.fieldKey}
        message={<TextWithHTML text={property.description} />}
        value={field.value ?? property.default}
        disabled={disabled}
      />
    );
  }

  return (
    <Label property={property} touched={meta.touched} error={meta.error}>
      <Control
        property={property}
        name={propertyPath}
        addUnfinishedFlow={addUnfinishedFlow}
        removeUnfinishedFlow={removeUnfinishedFlow}
        unfinishedFlows={unfinishedFlows}
        disabled={disabled}
      />
    </Label>
  );
};

export { PropertySection };
