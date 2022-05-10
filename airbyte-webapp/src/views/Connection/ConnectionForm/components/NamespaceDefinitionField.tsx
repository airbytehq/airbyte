import { FieldProps, useField } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { ControlLabels, DropDown } from "components";

import { ConnectionNamespaceDefinition } from "core/domain/connection";

import { LeftFieldCol, RightFieldCol, FlexRow } from "../ConnectionForm";

export const StreamOptions = [
  {
    value: ConnectionNamespaceDefinition.Source,
    label: <FormattedMessage id="connectionForm.sourceFormat" />,
    testId: "namespaceDefinition-source",
  },
  {
    value: ConnectionNamespaceDefinition.Destination,
    label: <FormattedMessage id="connectionForm.destinationFormat" />,
    testId: "namespaceDefinition-destination",
  },
  {
    value: ConnectionNamespaceDefinition.CustomFormat,
    label: <FormattedMessage id="connectionForm.customFormat" />,
    testId: "namespaceDefinition-customformat",
  },
];

export const NamespaceDefinitionField: React.FC<FieldProps<string>> = ({ field, form }) => {
  const [, meta] = useField(field.name);

  return (
    <FlexRow>
      <LeftFieldCol>
        <ControlLabels
          nextLine
          error={!!meta.error && meta.touched}
          labelAdditionLength={0}
          label={<FormattedMessage id="connectionForm.namespaceDefinition.title" />}
          message={<FormattedMessage id="connectionForm.namespaceDefinition.subtitle" />}
        />
      </LeftFieldCol>
      <RightFieldCol>
        <DropDown
          name="namespaceDefinition"
          error={!!meta.error && meta.touched}
          options={StreamOptions}
          value={field.value}
          onChange={({ value }) => form.setFieldValue(field.name, value)}
        />
      </RightFieldCol>
    </FlexRow>
  );
};
