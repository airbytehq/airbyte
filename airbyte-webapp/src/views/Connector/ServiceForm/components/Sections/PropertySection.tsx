import { useField } from "formik";
import React from "react";

import { LabeledSwitch } from "components";

import { FormBaseItem } from "core/form/types";

import { useServiceForm } from "../../serviceFormContext";
import { Control } from "../Property/Control";
import { PropertyLabel } from "../Property/PropertyLabel";
import styles from "./PropertySection.module.scss";

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

  const labelText = property.title || property.fieldKey;

  if (property.type === "boolean") {
    return (
      <LabeledSwitch
        {...field}
        label={<PropertyLabel className={styles.switchLabel} property={property} label={labelText} optional={false} />}
        value={field.value ?? property.default}
        disabled={disabled}
      />
    );
  }

  return (
    <PropertyLabel property={property} label={labelText} touched={meta.touched} error={meta.error}>
      <Control
        property={property}
        name={propertyPath}
        addUnfinishedFlow={addUnfinishedFlow}
        removeUnfinishedFlow={removeUnfinishedFlow}
        unfinishedFlows={unfinishedFlows}
        disabled={disabled}
      />
    </PropertyLabel>
  );
};

export { PropertySection };
