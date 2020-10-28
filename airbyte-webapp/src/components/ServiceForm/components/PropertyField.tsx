import React, { useCallback } from "react";
import { Field, FieldProps } from "formik";
import { FormattedHTMLMessage, useIntl } from "react-intl";

import LabeledInput from "../../LabeledInput";
import LabeledDropDown from "../../LabeledDropDown";
import { propertiesType } from "../../../core/resources/SourceSpecification";
import LabeledToggle from "../../LabeledToggle";

type IProps = {
  condition: propertiesType;
  property: string;
  setFieldValue: (field: string, value: string) => void;
  isRequired?: boolean;
};

const PropertyField: React.FC<IProps> = ({
  property,
  condition,
  setFieldValue,
  isRequired
}) => {
  const formatMessage = useIntl().formatMessage;

  const onSetValue = useCallback(
    selectedItem => setFieldValue(property, selectedItem.value),
    [property, setFieldValue]
  );

  const defaultLabel = `${formatMessage({
    id: `form.${property}`,
    defaultMessage: property
  })}`;

  const fieldValue = `${condition.title || defaultLabel}${
    isRequired ? " *" : ""
  }`;

  if (condition.type === "boolean") {
    return (
      <Field name={property}>
        {({ field }: FieldProps<string>) => (
          <LabeledToggle
            {...field}
            label={condition.title || defaultLabel}
            message={
              <FormattedHTMLMessage
                id="1"
                defaultMessage={condition.description}
              />
            }
            placeholder={condition.examples?.[0]}
            value={field.value || condition.default}
          />
        )}
      </Field>
    );
  }

  if (condition.enum) {
    return (
      <Field name={property}>
        {({ field }: FieldProps<string>) => (
          <LabeledDropDown
            {...field}
            label={fieldValue}
            message={
              condition.description ? (
                <FormattedHTMLMessage
                  id="1"
                  defaultMessage={condition.description}
                />
              ) : null
            }
            placeholder={condition.examples?.[0]}
            filterPlaceholder={formatMessage({
              id: "form.searchName"
            })}
            data={condition.enum.map((dataItem: string) => ({
              text: dataItem,
              value: dataItem
            }))}
            onSelect={onSetValue}
            value={field.value || condition.default}
          />
        )}
      </Field>
    );
  }

  return (
    <Field name={property}>
      {({ field }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          autoComplete="off"
          label={fieldValue}
          message={
            condition.description ? (
              <FormattedHTMLMessage
                id="1"
                defaultMessage={condition.description}
              />
            ) : null
          }
          placeholder={condition.examples?.[0]}
          type={condition.type === "integer" ? "number" : "text"}
          value={field.value || condition.default}
        />
      )}
    </Field>
  );
};

export default PropertyField;
