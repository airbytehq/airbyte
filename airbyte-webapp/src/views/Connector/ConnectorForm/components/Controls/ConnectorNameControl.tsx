import { useField } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Input } from "components/ui/Input";

import { FormBaseItem } from "core/form/types";

import { PropertyError } from "../Property/PropertyError";
import { PropertyLabel } from "../Property/PropertyLabel";

interface ConnectorNameControlProps {
  property: FormBaseItem;
  formType: "source" | "destination";
  disabled?: boolean;
}

export const ConnectorNameControl: React.FC<ConnectorNameControlProps> = ({ property, formType, disabled }) => {
  const { formatMessage } = useIntl();
  const [field, fieldMeta] = useField(property.path);

  const hasError = !!fieldMeta.error && fieldMeta.touched;

  return (
    <PropertyLabel
      property={property}
      label={<FormattedMessage id={`form.${formType}Name`} />}
      description={formatMessage({
        id: `form.${formType}Name.message`,
      })}
    >
      <Input
        {...field}
        error={hasError}
        type="text"
        placeholder={formatMessage({
          id: `form.${formType}Name.placeholder`,
        })}
        disabled={disabled}
      />
      {hasError && (
        <PropertyError>
          {formatMessage({
            id: fieldMeta.error,
          })}
        </PropertyError>
      )}
    </PropertyLabel>
  );
};
