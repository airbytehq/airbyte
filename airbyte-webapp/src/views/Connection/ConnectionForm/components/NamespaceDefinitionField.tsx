import { FieldProps, useField } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { ControlLabels, DropDown } from "components";

import { NamespaceDefinitionType } from "../../../../core/request/GeneratedApi";

export const StreamOptions = [
  {
    value: NamespaceDefinitionType.source,
    label: <FormattedMessage id="connectionForm.sourceFormat" />,
    testId: "namespaceDefinition-source",
  },
  {
    value: NamespaceDefinitionType.destination,
    label: <FormattedMessage id="connectionForm.destinationFormat" />,
    testId: "namespaceDefinition-destination",
  },
  {
    value: NamespaceDefinitionType.customformat,
    label: <FormattedMessage id="connectionForm.customFormat" />,
    testId: "namespaceDefinition-customformat",
  },
];

const NamespaceDefinitionField: React.FC<FieldProps<string>> = ({ field, form }) => {
  const [, meta] = useField(field.name);

  return (
    <ControlLabels
      nextLine
      error={!!meta.error && meta.touched}
      labelAdditionLength={0}
      label={<FormattedMessage id="connectionForm.namespaceDefinition.title" />}
      message={<FormattedMessage id="connectionForm.namespaceDefinition.subtitle" />}
    >
      <DropDown
        name="namespaceDefinition"
        error={!!meta.error && meta.touched}
        options={StreamOptions}
        value={field.value}
        onChange={({ value }) => form.setFieldValue(field.name, value)}
      />
    </ControlLabels>
  );
};

export { NamespaceDefinitionField };
