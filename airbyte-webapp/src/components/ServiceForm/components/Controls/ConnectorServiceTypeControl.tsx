import React, { useCallback, useMemo } from "react";
import { useIntl } from "react-intl";
import { useField } from "formik";
import styled from "styled-components";
import { ControlLabels, DropDown, DropDownRow, ImageBlock } from "components";

import { FormBaseItem } from "core/form/types";
import Instruction from "./Instruction";
import { SourceDefinition } from "core/resources/SourceDefinition";
import { DestinationDefinition } from "core/resources/DestinationDefinition";
import { isSourceDefinition } from "core/domain/connector/source";

const DropdownLabels = styled(ControlLabels)`
  max-width: 202px;
`;

const ConnectorServiceTypeControl: React.FC<{
  property: FormBaseItem;
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
          onSelect={handleSelect}
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
