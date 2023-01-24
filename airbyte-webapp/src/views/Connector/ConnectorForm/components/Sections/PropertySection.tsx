import React from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";

import { LabeledSwitch } from "components";

import { FormBaseItem } from "core/form/types";

import { Control } from "../Property/Control";
import { PropertyError } from "../Property/PropertyError";
import { PropertyLabel } from "../Property/PropertyLabel";
import styles from "./PropertySection.module.scss";

interface PropertySectionProps {
  property: FormBaseItem;
  path?: string;
  disabled?: boolean;
}

export const PropertySection: React.FC<PropertySectionProps> = ({ property, path, disabled }) => {
  const propertyPath = path ?? property.path;
  const { register, watch, getFieldState } = useFormContext();

  const meta = getFieldState(propertyPath);
  const fieldValue = watch(propertyPath);

  const labelText = property.title || property.fieldKey;

  if (property.type === "boolean") {
    const switchId = `switch-${propertyPath}`;
    return (
      <LabeledSwitch
        {...register(propertyPath)}
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
        value={fieldValue ?? property.default}
        disabled={disabled}
      />
    );
  }

  const hasError = !!meta.error && meta.isTouched;

  const errorValues = meta.error?.message === "form.pattern.error" ? { pattern: property.pattern } : undefined;
  const errorMessage = <FormattedMessage id={meta.error?.message} values={errorValues} />;

  return (
    <PropertyLabel className={styles.defaultLabel} property={property} label={labelText}>
      <Control property={property} name={propertyPath} disabled={disabled} error={hasError} />
      {hasError && <PropertyError>{errorMessage}</PropertyError>}
    </PropertyLabel>
  );
};
