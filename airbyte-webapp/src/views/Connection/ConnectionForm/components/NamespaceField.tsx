import React, { useMemo } from "react";
import { Field, FieldProps } from "formik";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ControlLabels, DropDown, Input } from "components";
import { ConnectionNamespaceDefinition } from "core/domain/connection";

const NamespaceConfigurationLabel = styled(ControlLabels)`
  width: 360px;
`;

const NamespaceFormatLabel = styled(ControlLabels)`
  margin-left: 21px;
`;

const Row = styled.div`
  display: flex;
  margin-bottom: 26px;
`;

const NamespaceField: React.FC<{}> = ({}) => {
  const definitions = useMemo(
    () => [
      {
        value: ConnectionNamespaceDefinition.Source,
        text: "source",
      },
      {
        value: ConnectionNamespaceDefinition.Destination,
        text: "destination",
      },
      {
        value: ConnectionNamespaceDefinition.CustomFormat,
        text: "custom",
      },
    ],
    []
  );
  return (
    <Row>
      <Field name="namespaceDefinition">
        {({ field, form }: FieldProps<string>) => (
          <>
            <NamespaceConfigurationLabel
              label={
                <FormattedMessage id="connectionForm.namespaceDefinition.title" />
              }
              message={
                <FormattedMessage id="connectionForm.namespaceDefinition.subtitle" />
              }
            >
              <DropDown
                data={definitions}
                value={field.value}
                onChange={({ value }) => form.setFieldValue(field.name, value)}
              />
            </NamespaceConfigurationLabel>
            {field.value === ConnectionNamespaceDefinition.CustomFormat && (
              <NamespaceFormatLabel
                label={
                  <FormattedMessage id="connectionForm.namespaceFormat.title" />
                }
                message={
                  <FormattedMessage id="connectionForm.namespaceFormat.subtitle" />
                }
              >
                <Field name="namespaceFormat" component={Input} />
              </NamespaceFormatLabel>
            )}
          </>
        )}
      </Field>
    </Row>
  );
};

export { NamespaceField };
