import React, { useMemo } from "react";
import { Formik, Form } from "formik";
import styled from "styled-components";
import { JSONSchema7 } from "json-schema";

import { IDataItem } from "components/DropDown/components/ListItem";
import FormContent from "./components/FormContent";
import BottomBlock from "./components/BottomBlock";
import EditControls from "./components/EditControls";

import {
  useBuildForm,
  FormInitialValues,
  useBuildUiWidgets,
  useConstructValidationSchema,
} from "./useBuildForm";
import { WidgetInfo, WidgetInfoProvider } from "./uiWidgetContext";
import { ConnectionConfiguration } from "core/domain/connection";

const FormContainer = styled(Form)`
  padding: 22px 27px 23px 24px;
`;

const defaultDataItemSort = (a: IDataItem, b: IDataItem) => {
  if (a.text < b.text) return -1;
  if (a.text > b.text) return 1;
  return 0;
};

type IProps = {
  additionBottomControls?: React.ReactNode;
  isLoading?: boolean;
  isEditMode?: boolean;
  allowChangeConnector?: boolean;
  dropDownData: Array<IDataItem>;
  onDropDownSelect?: (id: string) => void;
  onSubmit: (values: {
    name: string;
    serviceType: string;
    frequency?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  formType: "source" | "destination" | "connection";
  formValues?: Partial<FormInitialValues>;
  hasSuccess?: boolean;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
  specifications?: JSONSchema7;
  documentationUrl?: string;
};

const ServiceForm: React.FC<IProps> = ({
  formType,
  dropDownData,
  specifications,
  formValues,
  onSubmit,
  onDropDownSelect,
  successMessage,
  errorMessage,
  documentationUrl,
  allowChangeConnector,
  hasSuccess,
  additionBottomControls,
  isLoading,
  isEditMode,
}) => {
  const { formFields, initialValues } = useBuildForm(
    formType,
    isLoading,
    formValues,
    specifications
  );

  const { uiWidgetsInfo, setUiWidgetsInfo } = useBuildUiWidgets(
    formFields,
    initialValues
  );

  // As validation schema depends on what path of oneOf is currently selected in jsonschema
  const validationSchema = useConstructValidationSchema(
    uiWidgetsInfo,
    specifications
  );

  const sortedDropDownData = useMemo(
    () => dropDownData.sort(defaultDataItemSort),
    [dropDownData]
  );

  return (
    <WidgetInfoProvider
      widgetsInfo={uiWidgetsInfo}
      setUiWidgetsInfo={setUiWidgetsInfo}
    >
      <Formik
        initialValues={initialValues}
        validateOnBlur={true}
        validateOnChange={true}
        validationSchema={validationSchema}
        onSubmit={async (values) =>
          onSubmit(validationSchema.cast(values, { stripUnknown: true }))
        }
      >
        {({
          isSubmitting,
          isValid,
          dirty,
          resetForm,
          validateForm,
          values,
        }) => (
          <FormContainer>
            <FormContent
              values={values}
              validateForm={validateForm}
              allowChangeConnector={allowChangeConnector}
              schema={validationSchema}
              dropDownData={sortedDropDownData}
              formType={formType}
              formFields={formFields}
              isEditMode={isEditMode}
              isLoadingSchema={isLoading}
              onChangeServiceType={onDropDownSelect}
              documentationUrl={documentationUrl}
            />

            {isEditMode ? (
              <WidgetInfo>
                {({ resetUiFormProgress }) => (
                  <EditControls
                    isSubmitting={isSubmitting}
                    isValid={isValid}
                    dirty={dirty}
                    errorMessage={errorMessage}
                    resetForm={() => {
                      resetForm();
                      resetUiFormProgress();
                    }}
                    successMessage={successMessage}
                  />
                )}
              </WidgetInfo>
            ) : (
              <BottomBlock
                isSubmitting={isSubmitting}
                errorMessage={errorMessage}
                isLoadSchema={isLoading}
                formType={formType}
                additionBottomControls={additionBottomControls}
                hasSuccess={hasSuccess}
              />
            )}
          </FormContainer>
        )}
      </Formik>
    </WidgetInfoProvider>
  );
};

export default ServiceForm;
