import { useField } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Input } from "components";

import { FormBaseItem } from "core/form/types";

import { PropertyLabel } from "../Property/PropertyLabel";

interface ConnnectorNameControlProps {
  property: FormBaseItem;
  formType: "source" | "destination";
  disabled?: boolean;
}

export const ConnectorNameControl: React.FC<ConnnectorNameControlProps> = ({ property, formType, disabled }) => {
  const { formatMessage } = useIntl();
  const [field, fieldMeta] = useField(property.path);

  return (
    <PropertyLabel
      property={{
        ...property,
        description: formatMessage({
          id: `form.${formType}Name.message`,
        }),
      }}
      label={<FormattedMessage id={`form.${formType}Name`} />}
      touched={fieldMeta.touched}
      error={fieldMeta.error}
    >
      <Input
        {...field}
        error={!!fieldMeta.error && fieldMeta.touched}
        type="text"
        placeholder={formatMessage({
          id: `form.${formType}Name.placeholder`,
        })}
        disabled={disabled}
      />
    </PropertyLabel>
  );
};
