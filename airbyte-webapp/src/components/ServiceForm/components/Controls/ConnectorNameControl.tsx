import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useField } from "formik";

import { Input, ControlLabels } from "components";
import { FormBaseItem } from "core/form/types";
import { useServiceForm } from "../../serviceFormContext";

const ConnectorNameControl: React.FC<{ property: FormBaseItem }> = ({
  property,
}) => {
  const formatMessage = useIntl().formatMessage;
  const [field, fieldMeta] = useField(property.path);
  const { formType } = useServiceForm();

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
      />
    </ControlLabels>
  );
};

export { ConnectorNameControl };
