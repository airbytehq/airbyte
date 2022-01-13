import React from "react";
import { FieldProps } from "formik";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { useConfig } from "config";

import { ControlLabels, DropDown } from "components";
import { ConnectionNamespaceDefinition } from "core/domain/connection";

const NamespaceConfigurationLabel = styled(ControlLabels)`
  & a {
    color: ${({ theme }) => theme.greyColor40};
  }
`;

const StreamOptions = [
  {
    value: ConnectionNamespaceDefinition.Source,
    label: <FormattedMessage id="connectionForm.sourceFormat" />,
  },
  {
    value: ConnectionNamespaceDefinition.Destination,
    label: <FormattedMessage id="connectionForm.destinationFormat" />,
  },
  {
    value: ConnectionNamespaceDefinition.CustomFormat,
    label: <FormattedMessage id="connectionForm.customFormat" />,
  },
];

const NamespaceDefinitionField: React.FC<FieldProps<string>> = ({
  field,
  form,
}) => {
  const config = useConfig();

  return (
    <NamespaceConfigurationLabel
      nextLine
      labelAdditionLength={0}
      label={<FormattedMessage id="connectionForm.namespaceDefinition.title" />}
      message={
        <FormattedMessage
          id="connectionForm.namespaceDefinition.subtitle"
          values={{
            lnk: (...lnk: React.ReactNode[]) => (
              <a
                target="_blank"
                rel="noreferrer"
                href={config.ui.namespaceLink}
              >
                {lnk}
              </a>
            ),
          }}
        />
      }
    >
      <DropDown
        options={StreamOptions}
        value={field.value}
        onChange={({ value }) => form.setFieldValue(field.name, value)}
      />
    </NamespaceConfigurationLabel>
  );
};

export { NamespaceDefinitionField };
