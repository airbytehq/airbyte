import React, { useEffect } from "react";

import { FormikProps, useField } from "formik";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { IDataItem } from "../../DropDown/components/ListItem";
import Instruction from "./Instruction";
import Spinner from "../../Spinner";
import { Property } from "./Property";
import { FormBaseItem, FormBlock } from "../../../core/form/types";
import { FormInitialValues } from "../useBuildForm";
import DropDown from "../../DropDown";
import { ControlLabels } from "../../LabeledControl";
import Input from "../../Input";
import LabeledToggle from "../../LabeledToggle";
import TextWithHTML from "../../TextWithHTML";
import { useWidgetInfo } from "../uiWidgetContext";
import ShowLoadingMessage from "./ShowLoadingMessage";
import Label from "../../Label";

type IProps = {
  schema: any;
  formFields: FormBlock[];
  dropDownData: Array<IDataItem>;
  isLoadingSchema?: boolean;
  isEditMode?: boolean;
  allowChangeConnector?: boolean;
  formType: "source" | "destination" | "connection";
  documentationUrl?: string;
  onChangeServiceType?: (id: string) => void;
} & Pick<FormikProps<FormInitialValues>, "values" | "validateForm">;

const FormItem = styled.div`
  margin-bottom: 27px;
`;

const FormItemGroupDropDown = styled(FormItem)`
  margin-top: -17px;
  background: ${({ theme }) => theme.whiteColor};
  padding: 0 5px;
  display: inline-block;
  vertical-align: middle;
  & > div {
    min-width: 180px;
    display: inline-block;
  }
`;

const FormItemGroup = styled(FormItem)`
  border: 2px solid ${({ theme }) => theme.greyColor20};
  box-sizing: border-box;
  border-radius: 8px;
  padding: 0 20px;
  margin-top: 41px;
`;

const GroupLabel = styled(Label)`
  width: auto;
  margin-right: 8px;
  display: inline-block;
`;

const DropdownLabels = styled(ControlLabels)`
  max-width: 202px;
`;

const LoaderContainer = styled.div`
  text-align: center;
  padding: 22px 0 23px;
`;

const LoadingMessage = styled.div`
  margin-top: 10px;
`;

const FormRow: React.FC<{ property: FormBaseItem } & IProps> = ({
  property,
  isEditMode,
  allowChangeConnector,
  formType,
  dropDownData,
  onChangeServiceType,
  documentationUrl
}) => {
  const formatMessage = useIntl().formatMessage;
  const { fieldName, fieldKey, meta } = property;
  const [field, , form] = useField(fieldName);

  if (fieldKey === "name") {
    return (
      <ControlLabels
        // error={!!fieldProps.meta.error && fieldProps.meta.touched}
        label={<FormattedMessage id="form.name" />}
        message={formatMessage({
          id: `form.${formType}Name.message`
        })}
      >
        <Input
          {...field}
          type="text"
          placeholder={formatMessage({
            id: `form.${formType}Name.placeholder`
          })}
        />
      </ControlLabels>
    );
  }

  if (fieldKey === "serviceType") {
    return (
      <>
        <DropdownLabels
          label={formatMessage({
            id: `form.${formType}Type`
          })}
        >
          <DropDown
            {...field}
            disabled={isEditMode && !allowChangeConnector}
            hasFilter
            placeholder={formatMessage({
              id: "form.selectConnector"
            })}
            filterPlaceholder={formatMessage({
              id: "form.searchName"
            })}
            data={dropDownData}
            onSelect={item => {
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
  } else {
  }

  if (property.type === "boolean") {
    return (
      <LabeledToggle
        {...field}
        label={property.title || property.fieldKey}
        message={<TextWithHTML text={property.description} />}
        value={field.value ?? property.default}
      />
    );
  }

  return <Property property={property} />;
};

const FormContent: React.FC<IProps> = props => {
  const {
    schema,
    dropDownData,
    values,
    isLoadingSchema,
    validateForm,
    formFields
  } = props;

  // Formik doesn't validate values again, when validationSchema was changed on the fly.
  useEffect(() => {
    validateForm();
  }, [validateForm, schema]);

  const { widgetsInfo, setUiWidgetsInfo } = useWidgetInfo();

  const renderFormMeta = (formMetaFields: FormBlock[]): React.ReactNode => {
    return formMetaFields.map(formField => {
      if (formField._type === "formGroup") {
        return renderFormMeta(formField.properties);
      }

      if (formField._type === "formCondition") {
        const currentlySelectedCondition =
          widgetsInfo[formField.fieldName]?.selectedItem;

        const label = formField.title || formField.fieldKey;

        return (
          <FormItemGroup key={`form-field-group-${formField.fieldKey}`}>
            <FormItemGroupDropDown key={`form-field-${formField.fieldKey}`}>
              {label ? <GroupLabel>{label}:</GroupLabel> : null}
              <DropDown
                data={Object.keys(formField.conditions).map(dataItem => ({
                  text: dataItem,
                  value: dataItem
                }))}
                onSelect={selectedItem =>
                  setUiWidgetsInfo(formField.fieldName, {
                    selectedItem: selectedItem.value
                  })
                }
                value={currentlySelectedCondition}
              />
            </FormItemGroupDropDown>
            {renderFormMeta([formField.conditions[currentlySelectedCondition]])}
          </FormItemGroup>
        );
      }

      return (
        <FormItem key={`form-field-${formField.fieldKey}`}>
          <FormRow {...props} property={formField} />
        </FormItem>
      );
    });
  };

  const service =
    dropDownData &&
    dropDownData.find(item => item.value === values.serviceType);

  return (
    <>
      {renderFormMeta(formFields)}
      {isLoadingSchema && (
        <LoaderContainer>
          <Spinner />
          <LoadingMessage>
            <ShowLoadingMessage connector={service?.text} />
          </LoadingMessage>
        </LoaderContainer>
      )}
    </>
  );
};

export default FormContent;
