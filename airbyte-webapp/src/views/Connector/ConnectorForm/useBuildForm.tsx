import { JSONSchema7, JSONSchema7Definition } from "json-schema";
import { useMemo } from "react";
import { useIntl } from "react-intl";
import { AnySchema } from "yup";

import {
  ConnectorDefinitionSpecification,
  ConnectorSpecification,
  SourceDefinitionSpecificationDraft,
} from "core/domain/connector";
import { isSourceDefinitionSpecificationDraft } from "core/domain/connector/source";
import { FormBuildError, isFormBuildError } from "core/form/FormBuildError";
import { jsonSchemaToFormBlock } from "core/form/schemaToFormBlock";
import { buildYupFormForJsonSchema } from "core/form/schemaToYup";
import { FormBlock, FormGroupItem } from "core/form/types";

import { ConnectorFormValues } from "./types";

export interface BuildFormHook {
  initialValues: ConnectorFormValues;
  formFields: FormBlock;
  validationSchema: AnySchema;
}

export function setDefaultValues(
  formGroup: FormGroupItem,
  values: Record<string, unknown>,
  options: { respectExistingValues: boolean } = { respectExistingValues: false }
) {
  formGroup.properties.forEach((property) => {
    if (property.const && (!options.respectExistingValues || !values[property.fieldKey])) {
      values[property.fieldKey] = property.const;
    }
    if (property.default && (!options.respectExistingValues || !values[property.fieldKey])) {
      values[property.fieldKey] = property.default;
    }
    switch (property._type) {
      case "formGroup":
        values[property.fieldKey] =
          options.respectExistingValues && values[property.fieldKey] ? values[property.fieldKey] : {};
        setDefaultValues(property, values[property.fieldKey] as Record<string, unknown>, options);
        break;
      case "formCondition":
        values[property.fieldKey] = {};
        let chosenCondition = property.conditions[0];
        // if default is set, try to find it in the list of possible selection const values.
        // if there is a match, default to this condition.
        // In all other cases, go with the first one.
        if (property.default) {
          const matchingConditionIndex = property.selectionConstValues.indexOf(property.default);
          if (matchingConditionIndex !== -1) {
            chosenCondition = property.conditions[matchingConditionIndex];
          }
        }

        setDefaultValues(chosenCondition, values[property.fieldKey] as Record<string, unknown>);
    }
  });
}

export function useBuildForm(
  isEditMode: boolean,
  formType: "source" | "destination",
  selectedConnectorDefinitionSpecification:
    | ConnectorDefinitionSpecification
    | SourceDefinitionSpecificationDraft
    | undefined,
  initialValues?: Partial<ConnectorFormValues>
): BuildFormHook {
  const { formatMessage } = useIntl();

  const isDraft =
    selectedConnectorDefinitionSpecification &&
    isSourceDefinitionSpecificationDraft(selectedConnectorDefinitionSpecification);

  try {
    const jsonSchema: JSONSchema7 = useMemo(() => {
      if (!selectedConnectorDefinitionSpecification) {
        return {
          type: "object",
          properties: {},
        };
      }
      const schema: JSONSchema7 = {
        type: "object",
        properties: {
          connectionConfiguration:
            selectedConnectorDefinitionSpecification.connectionSpecification as JSONSchema7Definition,
        },
      };
      if (isDraft) {
        return schema;
      }
      schema.properties = {
        name: {
          type: "string",
          title: formatMessage({ id: `form.${formType}Name` }),
          description: formatMessage({ id: `form.${formType}Name.message` }),
        },
        ...schema.properties,
      };
      schema.required = ["name"];
      return schema;
    }, [formType, formatMessage, isDraft, selectedConnectorDefinitionSpecification]);

    const formFields = useMemo<FormBlock>(() => jsonSchemaToFormBlock(jsonSchema), [jsonSchema]);

    if (formFields._type !== "formGroup") {
      throw new FormBuildError("connectorForm.error.topLevelNonObject");
    }

    const validationSchema = useMemo(() => buildYupFormForJsonSchema(jsonSchema, formFields), [formFields, jsonSchema]);

    const startValues = useMemo<ConnectorFormValues>(() => {
      let baseValues = {
        name: "",
        connectionConfiguration: {},
        ...initialValues,
      };

      if (isDraft) {
        try {
          baseValues = validationSchema.cast(baseValues, { stripUnknown: true });
        } catch {
          // cast did not work which can happen if there are unexpected values in the form. Reset form in this case
          baseValues.connectionConfiguration = {};
        }
      }

      if (isEditMode) {
        return baseValues;
      }

      setDefaultValues(formFields, baseValues as Record<string, unknown>, { respectExistingValues: Boolean(isDraft) });

      return baseValues;
    }, [formFields, initialValues, isDraft, isEditMode, validationSchema]);

    return {
      initialValues: startValues,
      formFields,
      validationSchema,
    };
  } catch (e) {
    // catch and re-throw form-build errors to enrich them with the connector id
    if (isFormBuildError(e)) {
      throw new FormBuildError(
        e.message,
        isDraft || !selectedConnectorDefinitionSpecification
          ? undefined
          : ConnectorSpecification.id(selectedConnectorDefinitionSpecification)
      );
    }
    throw e;
  }
}
