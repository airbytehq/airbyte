import React from "react";
import { useField } from "formik";
import { useIntl } from "react-intl";

import LabeledInput from "../../LabeledInput";
import LabeledDropDown from "../../LabeledDropDown";
import LabeledToggle from "../../LabeledToggle";
import TextWithHTML from "../../TextWithHTML";
import { FormBaseItem } from "../../../core/form/types";

type IProps = {
  property: FormBaseItem;
};

const PropertyField: React.FC<IProps> = ({ property }) => {
  const formatMessage = useIntl().formatMessage;
  const { fieldName, fieldKey } = property;
  const [field, { error }, form] = useField(fieldName);

  const defaultLabel = formatMessage({
    id: `form.${fieldKey}`,
    defaultMessage: fieldKey
  });

  const label = `${property.title || defaultLabel}${
    property.isRequired ? " *" : ""
  }`;

  // TODO: fix
  const placeholder = property.examples?.[0] as string;

  if (property.type === "boolean") {
    return (
      <LabeledToggle
        {...field}
        label={property.title || defaultLabel}
        message={<TextWithHTML text={property.description} />}
        placeholder={placeholder}
        value={field.value || property.default}
      />
    );
  } else if (property.enum) {
    return (
      <LabeledDropDown
        {...field}
        error={!!error}
        label={label}
        message={
          property.description ? (
            <TextWithHTML text={property.description} />
          ) : null
        }
        placeholder={placeholder}
        filterPlaceholder={formatMessage({
          id: "form.searchName"
        })}
        data={property.enum.map(dataItem => ({
          text: dataItem?.toString() ?? "",
          value: dataItem?.toString() ?? ""
        }))}
        onSelect={selectedItem => form.setValue(selectedItem.value)}
        value={field.value || property.default}
      />
    );
  } else {
    return (
      <LabeledInput
        {...field}
        error={!!error}
        autoComplete="off"
        label={label}
        message={
          property.description ? (
            <TextWithHTML text={property.description} />
          ) : null
        }
        placeholder={placeholder}
        type={property.type === "integer" ? "number" : "text"}
        value={field.value || property.default}
      />
    );
  }
};

export default PropertyField;
