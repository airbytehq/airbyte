import React, { useMemo } from "react";

import { useField } from "formik";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import {
  ControlLabels,
  DropDown,
  DropDownRow,
  Input,
  LabeledToggle,
  TextWithHTML,
} from "components";
import { FormBaseItem } from "core/form/types";
import Instruction from "./Instruction";
import { Label } from "./Property/Label";
import { Control } from "./Property/Control";
import { useServiceForm } from "../serviceFormContext";

const DropdownLabels = styled(ControlLabels)`
  max-width: 202px;
`;

const ServiceTypeProperty: React.FC<{ property: FormBaseItem }> = ({
  property,
}) => {
  const formatMessage = useIntl().formatMessage;
  const { fieldName, meta } = property;
  const [field, fieldMeta, form] = useField(fieldName);

  const {
    formType,
    isEditMode,
    allowChangeConnector,
    onChangeServiceType,
    dropDownData,
    documentationUrl,
  } = useServiceForm();

  const sortedDropDownData = useMemo(
    () => dropDownData.sort(DropDownRow.defaultDataItemSort),
    [dropDownData]
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
          onSelect={(item) => {
            form.setValue(item.value);
            if (onChangeServiceType) {
              onChangeServiceType(item.value);
            }
          }}
        />
      </DropdownLabels>
      {field.value && meta?.includeInstruction && (
        <Instruction
          serviceId={field.value}
          dropDownData={dropDownData}
          documentationUrl={documentationUrl}
        />
      )}
    </>
  );
};

const Property: React.FC<{ property: FormBaseItem }> = ({ property }) => {
  const formatMessage = useIntl().formatMessage;
  const { fieldName, fieldKey } = property;
  const [field, fieldMeta] = useField(fieldName);
  const {
    addUnfinishedSecret,
    removeUnfinishedSecret,
    unfinishedSecrets,
    formType,
  } = useServiceForm();

  if (fieldKey === "name") {
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
  } else if (fieldKey === "serviceType") {
    return <ServiceTypeProperty property={property} />;
  } else if (property.type === "boolean") {
    return (
      <LabeledToggle
        {...field}
        label={property.title || property.fieldKey}
        message={<TextWithHTML text={property.description} />}
        value={field.value ?? property.default}
      />
    );
  }

  return (
    <Label property={property}>
      <Control
        property={property}
        addUnfinishedSecret={addUnfinishedSecret}
        removeUnfinishedSecret={removeUnfinishedSecret}
        unfinishedSecrets={unfinishedSecrets}
      />
    </Label>
  );
};

export { Property };
