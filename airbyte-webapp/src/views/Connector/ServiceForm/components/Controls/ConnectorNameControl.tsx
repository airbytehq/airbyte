import { useField } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Input } from "components";

import { FormBaseItem } from "core/form/types";

import { PropertyLabel } from "../Property/PropertyLabel";
import { PropertyError } from "../Sections/PropertyError";

interface ConnnectorNameControlProps {
  property: FormBaseItem;
  formType: "source" | "destination";
  disabled?: boolean;
}

export const ConnectorNameControl: React.FC<ConnnectorNameControlProps> = ({ property, formType, disabled }) => {
  const { formatMessage } = useIntl();
  const [field, fieldMeta] = useField(property.path);

  const displayError = !!fieldMeta.error && fieldMeta.touched;

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
        error={displayError}
        type="text"
        placeholder={formatMessage({
          id: `form.${formType}Name.placeholder`,
        })}
        disabled={disabled}
      />
      {displayError && (
        <PropertyError>
          {formatMessage({
            id: fieldMeta.error,
          })}
        </PropertyError>
      )}
    </PropertyLabel>
  );
};
