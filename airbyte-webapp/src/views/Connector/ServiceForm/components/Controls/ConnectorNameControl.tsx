import { useField } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Input, ControlLabels } from "components";

import { FormBaseItem } from "core/form/types";

interface ConnnectorNameControlProps {
  property: FormBaseItem;
  formType: "source" | "destination";
  disabled?: boolean;
}

export const ConnectorNameControl: React.FC<ConnnectorNameControlProps> = ({ property, formType, disabled }) => {
  const { formatMessage } = useIntl();
  const [field, fieldMeta] = useField(property.path);

  return (
    <ControlLabels
      error={!!fieldMeta.error && fieldMeta.touched}
      label={<FormattedMessage id="form.name" />}
      message={formatMessage({
        id: `form.${formType}Name.message`,
      })}
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
    </ControlLabels>
  );
};
