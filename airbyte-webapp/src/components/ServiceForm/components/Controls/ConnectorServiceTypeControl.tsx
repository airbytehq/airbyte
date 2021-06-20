import React, { useCallback, useMemo } from "react";
import { useIntl } from "react-intl";
import { useField } from "formik";
import styled from "styled-components";
import { ControlLabels, DropDown, DropDownRow, ImageBlock } from "components";
import List from "react-widgets/lib/List";

import { FormBaseItem } from "core/form/types";
import Instruction from "./Instruction";
import { SourceDefinition } from "core/resources/SourceDefinition";
import { DestinationDefinition } from "core/resources/DestinationDefinition";
import { isSourceDefinition } from "core/domain/connector/source";

const DropdownLabels = styled(ControlLabels)`
  max-width: 202px;
`;

const BottomElement = styled.div`
  background: ${(props) => props.theme.greyColor0};
  padding: 6px 16px 8px;
  width: 100%;
  min-height: 34px;
  border-top: 1px solid ${(props) => props.theme.greyColor20};
`;

const ConnectorList = React.forwardRef(
  ({ bottomBlock, ...listProps }: any, ref) => (
    <>
      <List ref={ref} {...listProps} />
      <BottomElement>{bottomBlock}</BottomElement>
    </>
  )
);

const ConnectorServiceTypeControl: React.FC<{
  property: FormBaseItem;
  bottomBlock?: React.ReactNode;
  formType: "source" | "destination";
  availableServices: (SourceDefinition | DestinationDefinition)[];
  isEditMode?: boolean;
  documentationUrl?: string;
  allowChangeConnector?: boolean;
  onChangeServiceType?: (id: string) => void;
}> = ({
  property,
  formType,
  isEditMode,
  allowChangeConnector,
  onChangeServiceType,
  availableServices,
  documentationUrl,
  bottomBlock,
}) => {
  const formatMessage = useIntl().formatMessage;
  const [field, fieldMeta, { setValue }] = useField(property.path);

  const sortedDropDownData = useMemo(
    () =>
      availableServices
        .map((item: SourceDefinition | DestinationDefinition) => ({
          text: item.name,
          value: isSourceDefinition(item)
            ? item.sourceDefinitionId
            : item.destinationDefinitionId,
          img: <ImageBlock img={item.icon} />,
        }))
        .sort(DropDownRow.defaultDataItemSort),
    [availableServices]
  );

  const selectedService = React.useMemo(
    () =>
      availableServices.find(
        (s) =>
          (isSourceDefinition(s)
            ? s.sourceDefinitionId
            : s.destinationDefinitionId) === field.value
      ),
    [field.value, availableServices]
  );

  const handleSelect = useCallback(
    (item: DropDownRow.IDataItem) => {
      setValue(item.value);
      if (onChangeServiceType) {
        onChangeServiceType(item.value);
      }
    },
    [setValue, onChangeServiceType]
  );

  return (
    <>
      <DropdownLabels
        label={formatMessage({
          id: `form.${formType}Type`,
        })}
      >
        <DropDown
          {...field}
          listComponent={ConnectorList}
          listProps={{ bottomBlock }}
          error={!!fieldMeta.error && fieldMeta.touched}
          disabled={isEditMode && !allowChangeConnector}
          hasFilter
          placeholder={formatMessage({
            id: "form.selectConnector",
          })}
          filterPlaceholder={formatMessage({
            id: "form.searchName",
          })}
          data={sortedDropDownData}
          onChange={handleSelect}
        />
      </DropdownLabels>
      {selectedService && documentationUrl && (
        <Instruction
          selectedService={selectedService}
          documentationUrl={documentationUrl}
        />
      )}
    </>
  );
};

export { ConnectorServiceTypeControl };
