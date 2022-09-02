import { useField } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { LabeledSwitch } from "components";

import { FormBaseItem } from "core/form/types";

import { useServiceForm } from "../../serviceFormContext";
import { Control } from "../Property/Control";
import { PropertyLabel } from "../Property/PropertyLabel";
import { PropertyError } from "./PropertyError";
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

  const displayError = !!meta.error && meta.touched;

  const errorValues = meta.error === "form.pattern.error" ? { pattern: property.pattern } : undefined;
  const errorMessage = <FormattedMessage id={meta.error} values={errorValues} />;

  return (
    <PropertyLabel property={property} label={labelText}>
      <Control
        property={property}
        name={propertyPath}
        addUnfinishedFlow={addUnfinishedFlow}
        removeUnfinishedFlow={removeUnfinishedFlow}
        unfinishedFlows={unfinishedFlows}
        disabled={disabled}
        error={displayError}
      />
      {displayError && <PropertyError>{errorMessage}</PropertyError>}
    </PropertyLabel>
  );
};

export { PropertySection };
