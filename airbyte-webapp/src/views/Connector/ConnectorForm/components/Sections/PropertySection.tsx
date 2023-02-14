import { useField } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { LabeledSwitch } from "components";

import { FormBaseItem } from "core/form/types";

import styles from "./PropertySection.module.scss";
import { Control } from "../Property/Control";
import { PropertyError } from "../Property/PropertyError";
import { PropertyLabel } from "../Property/PropertyLabel";

interface PropertySectionProps {
  property: FormBaseItem;
  path?: string;
  disabled?: boolean;
}

export const PropertySection: React.FC<PropertySectionProps> = ({ property, path, disabled }) => {
  const propertyPath = path ?? property.path;
  const formikBag = useField(propertyPath);
  const [field, meta] = formikBag;

  const labelText = property.title || property.fieldKey;

  if (property.type === "boolean") {
    const switchId = `switch-${field.name}`;
    return (
      <LabeledSwitch
        {...field}
        id={switchId}
        label={
          <PropertyLabel
            className={styles.switchLabel}
            property={property}
            label={labelText}
            optional={false}
            htmlFor={switchId}
          />
        }
        value={field.value ?? property.default}
        disabled={disabled}
      />
    );
  }

  const hasError = !!meta.error && meta.touched;

  const errorValues = meta.error === "form.pattern.error" ? { pattern: property.pattern } : undefined;
  const errorMessage = <FormattedMessage id={meta.error} values={errorValues} />;

  return (
    <PropertyLabel className={styles.defaultLabel} property={property} label={labelText}>
      <Control property={property} name={propertyPath} disabled={disabled} error={hasError} />
      {hasError && <PropertyError>{errorMessage}</PropertyError>}
    </PropertyLabel>
  );
};
