import React from "react";
import { useField } from "formik";
import { FormattedHTMLMessage, useIntl } from "react-intl";

import LabeledInput from "../../LabeledInput";
import LabeledDropDown from "../../LabeledDropDown";
import LabeledToggle from "../../LabeledToggle";
import { FormBaseItem } from "../../../core/form/types";

type IProps = {
  condition: FormBaseItem;
};

const PropertyField: React.FC<IProps> = ({ condition }) => {
  const formatMessage = useIntl().formatMessage;
  const { fieldName, fieldKey } = condition;
  const [field, , { setValue }] = useField(fieldName);

  const defaultLabel = formatMessage({
    id: `form.${fieldKey}`,
    defaultMessage: fieldKey
  });

  const label = `${condition.title || defaultLabel}${
    condition.isRequired ? " *" : ""
  }`;

  // TODO: fix
  const placeholder = condition.examples?.[0] as string;

  if (condition.type === "boolean") {
    return (
      <LabeledToggle
        {...field}
        label={condition.title || defaultLabel}
        message={
          <FormattedHTMLMessage id="1" defaultMessage={condition.description} />
        }
        placeholder={placeholder}
        value={field.value || condition.default}
      />
    );
  } else if (condition.enum) {
    return (
      <LabeledDropDown
        {...field}
        label={label}
        message={
          condition.description ? (
            <FormattedHTMLMessage
              id="1"
              defaultMessage={condition.description}
            />
          ) : null
        }
        placeholder={placeholder}
        filterPlaceholder={formatMessage({
          id: "form.searchName"
        })}
        data={condition.enum.map(dataItem => ({
          text: dataItem?.toString() ?? "",
          value: dataItem?.toString() ?? ""
        }))}
        onSelect={selectedItem => setValue(selectedItem.value)}
        value={field.value || condition.default}
      />
    );
  } else {
    return (
      <LabeledInput
        {...field}
        autoComplete="off"
        label={label}
        message={
          condition.description ? (
            <FormattedHTMLMessage
              id="1"
              defaultMessage={condition.description}
            />
          ) : null
        }
        placeholder={placeholder}
        type={condition.type === "integer" ? "number" : "text"}
        value={field.value || condition.default}
      />
    );
  }
};

export default PropertyField;
