import React, { useCallback, useMemo } from "react";
import { useIntl } from "react-intl";
import { useField } from "formik";
import styled from "styled-components";
import { DropDown, DropDownRow, ControlLabels } from "components";

import { FormBaseItem } from "core/form/types";
import { useServiceForm } from "../../serviceFormContext";

const DropdownLabels = styled(ControlLabels)`
  max-width: 202px;
`;

const ConnectorServiceTypeControl: React.FC<{ property: FormBaseItem }> = ({
  property,
}) => {
  const formatMessage = useIntl().formatMessage;
  const [field, fieldMeta, { setValue }] = useField(property.path);

  const {
    formType,
    isEditMode,
    allowChangeConnector,
    onChangeServiceType,
    dropDownData,
  } = useServiceForm();

  const sortedDropDownData = useMemo(
    () => dropDownData.sort(DropDownRow.defaultDataItemSort),
    [dropDownData]
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
      {/*TODO: figure out when we want to include instruction*/}
      {/*{field.value && includeInstruction && (*/}
      {/*  <Instruction*/}
      {/*    serviceId={field.value}*/}
      {/*    dropDownData={dropDownData}*/}
      {/*    documentationUrl={documentationUrl}*/}
      {/*  />*/}
      {/*)}*/}
    </>
  );
};

export { ConnectorServiceTypeControl };
