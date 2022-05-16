import { useField } from "formik";
import React from "react";

import { LabeledToggle, TextWithHTML } from "components";

import { FormBaseItem } from "core/form/types";

import { useServiceForm } from "../../serviceFormContext";
import { Control } from "../Property/Control";
import { Label } from "../Property/Label";

const PropertySection: React.FC<{ property: FormBaseItem; path?: string }> = ({ property, path }) => {
  const propertyPath = path ?? property.path;
  const formikBag = useField(propertyPath);
  const [field, meta] = formikBag;
  const { addUnfinishedFlow, removeUnfinishedFlow, unfinishedFlows, widgetsInfo } = useServiceForm();

  const overriddenComponent = widgetsInfo[propertyPath]?.component;
  if (overriddenComponent) {
    return <>{overriddenComponent(property)}</>;
  }

  if (property.type === "boolean") {
    return (
      <LabeledToggle
        {...field}
        label={property.title || property.fieldKey}
        message={<TextWithHTML text={property.description} />}
        value={field.value ?? property.default}
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
      />
    </Label>
  );
};

export { PropertySection };
