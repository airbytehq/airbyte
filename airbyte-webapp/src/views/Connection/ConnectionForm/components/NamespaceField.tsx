import React, { useMemo } from "react";
import { Field, FieldProps } from "formik";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { ControlLabels, DropDown, Input } from "components";
import { ConnectionNamespaceDefinition } from "core/domain/connection";

const NamespaceConfigurationLabel = styled(ControlLabels)`
  flex: 3 0 0;
  & a {
    color: ${({ theme }) => theme.greyColor40};
  }
`;

const NamespaceFormatLabel = styled(ControlLabels)`
  margin-left: 21px;
  flex: 5 0 0;
`;

const Row = styled.div`
  display: flex;
  margin-bottom: 26px;
`;

const NamespaceField: React.FC<{}> = ({}) => {
  const formatMessage = useIntl().formatMessage;

  const definitions = useMemo(
    () => [
      {
        value: ConnectionNamespaceDefinition.Source,
        text: <FormattedMessage id="connectionForm.sourceFormat" />,
      },
      {
        value: ConnectionNamespaceDefinition.Destination,
        text: <FormattedMessage id="connectionForm.destinationFormat" />,
      },
      {
        value: ConnectionNamespaceDefinition.CustomFormat,
        text: <FormattedMessage id="connectionForm.customFormat" />,
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
              labelAdditionLength={0}
              label={
                <FormattedMessage id="connectionForm.namespaceDefinition.title" />
              }
              message={
                <FormattedMessage
                  id="connectionForm.namespaceDefinition.subtitle"
                  values={{
                    lnk: (...lnk: React.ReactNode[]) => (
                      // TODO: add href url
                      <a target="_blank" href="/">
                        {lnk}
                      </a>
                    ),
                  }}
                />
              }
            >
              <DropDown
                data={definitions}
                value={field.value}
                onChange={({ value }) => form.setFieldValue(field.name, value)}
              />
            </NamespaceConfigurationLabel>
            {field.value === ConnectionNamespaceDefinition.CustomFormat ? (
              <NamespaceFormatLabel
                nextLine
                label={
                  <FormattedMessage id="connectionForm.namespaceFormat.title" />
                }
                message={
                  <FormattedMessage id="connectionForm.namespaceFormat.subtitle" />
                }
              >
                <Field
                  name="namespaceFormat"
                  component={Input}
                  placeholder={formatMessage({
                    id: "connectionForm.namespaceFormat.placeholder",
                  })}
                />
              </NamespaceFormatLabel>
            ) : (
              <NamespaceFormatLabel as="div" />
            )}
          </>
        )}
      </Field>
    </Row>
  );
};

export { NamespaceField };
