import { Field, FieldProps, useFormikContext } from "formik";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { FlexContainer } from "components/ui/Flex";
import { Text } from "components/ui/Text";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { useModalService } from "hooks/services/Modal";

import { FormikConnectionFormValues } from "./formConfig";
import { FormFieldWrapper } from "./FormFieldWrapper";
import { ControlLabels } from "../../LabeledControl";
import {
  DestinationNamespaceFormValueType,
  DestinationNamespaceModal,
} from "../DestinationNamespaceModal/DestinationNamespaceModal";

const namespaceDefinitionOptions = {
  [NamespaceDefinitionType.destination]: "destinationFormat",
  [NamespaceDefinitionType.source]: "sourceFormat",
  [NamespaceDefinitionType.customformat]: "customFormat",
};

/**
 * Destination namespace definition field for new stream table
 * will replace NamespaceDefinitionField.tsx in future
 * TODO: rename to NamespaceDefinitionField when the old version will be removed
 */
export const NamespaceDefinitionFieldNext = () => {
  const { mode } = useConnectionFormService();
  const { openModal, closeModal } = useModalService();

  const formikProps = useFormikContext<FormikConnectionFormValues>();

  const destinationNamespaceChange = (value: DestinationNamespaceFormValueType) => {
    formikProps.setFieldValue("namespaceDefinition", value.namespaceDefinition);

    if (value.namespaceDefinition === NamespaceDefinitionType.customformat) {
      formikProps.setFieldValue("namespaceFormat", value.namespaceFormat);
    }
  };

  const destinationModalContent = (
    <DestinationNamespaceModal
      initialValues={{
        namespaceDefinition: formikProps.values.namespaceDefinition,
        namespaceFormat: formikProps.values.namespaceFormat,
      }}
      onCloseModal={closeModal}
      onSubmit={destinationNamespaceChange}
    />
  );

  return (
    <Field name="namespaceDefinition">
      {({ field }: FieldProps<NamespaceDefinitionType>) => (
        <FormFieldWrapper>
          <ControlLabels
            label={<FormattedMessage id="connectionForm.namespaceDefinition.title" />}
            infoTooltipContent={<FormattedMessage id="connectionForm.namespaceDefinition.subtitle" />}
          />
          <FlexContainer alignItems="center" justifyContent="space-between">
            <Text>
              <FormattedMessage id={`connectionForm.${namespaceDefinitionOptions[field.value]}`} />
            </Text>
            <Button
              type="button"
              variant="secondary"
              disabled={mode === "readonly"}
              onClick={() =>
                openModal({
                  size: "lg",
                  title: <FormattedMessage id="connectionForm.modal.destinationNamespace.title" />,
                  content: () => destinationModalContent,
                })
              }
            >
              <FormattedMessage id="form.edit" />
            </Button>
          </FlexContainer>
        </FormFieldWrapper>
      )}
    </Field>
  );
};
