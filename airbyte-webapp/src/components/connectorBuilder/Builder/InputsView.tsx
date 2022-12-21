import { faGear, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Form, Formik, useField, useFormikContext } from "formik";
import { JSONSchema7 } from "json-schema";
import { useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useEffectOnce } from "react-use";
import * as yup from "yup";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { InfoBox } from "components/ui/InfoBox";
import { Modal, ModalBody, ModalFooter } from "components/ui/Modal";
import { Text } from "components/ui/Text";

import { FormikPatch } from "core/form/FormikPatch";

import { BuilderFormInput, BuilderFormValues, getInferredInputs } from "../types";
import { BuilderConfigView } from "./BuilderConfigView";
import { BuilderField } from "./BuilderField";
import styles from "./InputsView.module.scss";

const supportedTypes = ["string", "integer", "number", "array", "boolean", "enum", "unknown"] as const;

interface InputInEditing {
  key: string;
  definition: JSONSchema7;
  required: boolean;
  isNew?: boolean;
  showDefaultValueField: boolean;
  type: typeof supportedTypes[number];
  isInferredInputOverride: boolean;
}

function sluggify(str: string) {
  return str.toLowerCase().replaceAll(/[^a-zA-Z\d]/g, "_");
}

function newInputInEditing(): InputInEditing {
  return {
    key: "",
    definition: {},
    required: false,
    isNew: true,
    showDefaultValueField: false,
    type: "string",
    isInferredInputOverride: false,
  };
}

function formInputToInputInEditing(
  { key, definition, required }: BuilderFormInput,
  isInferredInputOverride: boolean
): InputInEditing {
  const supportedType = supportedTypes.find((type) => type === definition.type) || "unknown";
  return {
    key,
    definition,
    required,
    isNew: false,
    showDefaultValueField: Boolean(definition.default),
    type: supportedType !== "unknown" && definition.enum ? "enum" : supportedType,
    isInferredInputOverride,
  };
}

function inputInEditingToFormInput({
  type,
  showDefaultValueField,
  isNew,
  ...values
}: InputInEditing): BuilderFormInput {
  return {
    ...values,
    definition: {
      ...values.definition,
      type: type === "enum" ? "string" : type === "unknown" ? values.definition.type : type,
      // only respect the enum values if the user explicitly selected enum as type
      enum: type === "enum" && values.definition.enum?.length ? values.definition.enum : undefined,
      default: showDefaultValueField ? values.definition.default : undefined,
    },
  };
}

export const InputsView: React.FC = () => {
  const { formatMessage } = useIntl();
  const { values, setFieldValue } = useFormikContext<BuilderFormValues>();
  const [inputs, , helpers] = useField<BuilderFormInput[]>("inputs");
  const [inputInEditing, setInputInEditing] = useState<InputInEditing | undefined>(undefined);
  const inferredInputs = useMemo(() => getInferredInputs(values), [values]);
  const usedKeys = useMemo(
    () => [...inputs.value, ...inferredInputs].map((input) => input.key),
    [inputs.value, inferredInputs]
  );
  const inputInEditValidation = useMemo(
    () =>
      yup.object().shape({
        // make sure key can only occur once
        key: yup
          .string()
          .notOneOf(
            inputInEditing?.isNew ? usedKeys : usedKeys.filter((key) => key !== inputInEditing?.key),
            "connectorBuilder.duplicateFieldID"
          ),
        required: yup.bool(),
        definition: yup.object().shape({
          title: yup.string().required("form.empty.error"),
        }),
      }),
    [inputInEditing?.isNew, inputInEditing?.key, usedKeys]
  );

  return (
    <BuilderConfigView heading={formatMessage({ id: "connectorBuilder.inputsTitle" })}>
      <Text centered className={styles.inputsDescription}>
        <FormattedMessage id="connectorBuilder.inputsDescription" />
      </Text>
      {(inputs.value.length > 0 || inferredInputs.length > 0) && (
        <Card withPadding className={styles.inputsCard}>
          <ol className={styles.list}>
            {inferredInputs.map((input) => (
              <InputItem input={input} setInputInEditing={setInputInEditing} isInferredInput />
            ))}
            {inputs.value.map((input) => (
              <InputItem input={input} setInputInEditing={setInputInEditing} isInferredInput={false} />
            ))}
          </ol>
        </Card>
      )}
      <Button
        className={styles.addInputButton}
        onClick={() => {
          setInputInEditing(newInputInEditing());
        }}
        icon={<FontAwesomeIcon icon={faPlus} />}
        iconPosition="left"
        variant="secondary"
      >
        <FormattedMessage id="connectorBuilder.addInputButton" />
      </Button>
      {inputInEditing && (
        <Formik
          initialValues={inputInEditing}
          validationSchema={inputInEditValidation}
          onSubmit={(values: InputInEditing) => {
            if (values.isInferredInputOverride) {
              setFieldValue(`inferredInputOverrides.${values.key}`, values.definition);
            } else {
              const newInput = inputInEditingToFormInput(values);
              helpers.setValue(
                inputInEditing.isNew
                  ? [...inputs.value, newInput]
                  : inputs.value.map((input) => (input.key === inputInEditing.key ? newInput : input))
              );
            }
            setInputInEditing(undefined);
          }}
        >
          <>
            <FormikPatch />
            <InputModal
              inputInEditing={inputInEditing}
              onDelete={() => {
                helpers.setValue(inputs.value.filter((input) => input.key !== inputInEditing.key));
                setInputInEditing(undefined);
              }}
              onClose={() => {
                setInputInEditing(undefined);
              }}
            />
          </>
        </Formik>
      )}
    </BuilderConfigView>
  );
};

const InputModal = ({
  inputInEditing,
  onClose,
  onDelete,
}: {
  inputInEditing: InputInEditing;
  onDelete: () => void;
  onClose: () => void;
}) => {
  const isInferredInputOverride = inputInEditing.isInferredInputOverride;
  const { isValid, values, setFieldValue, setTouched } = useFormikContext<InputInEditing>();

  const { formatMessage } = useIntl();
  useEffectOnce(() => {
    // key input is always touched so errors are shown right away as it will be auto-set by the user changing the title
    setTouched({ key: true });
  });

  return (
    <Modal
      size="sm"
      title={
        <FormattedMessage
          id={inputInEditing.isNew ? "connectorBuilder.inputModal.newTitle" : "connectorBuilder.inputModal.editTitle"}
        />
      }
      onClose={onClose}
    >
      <Form>
        <ModalBody className={styles.inputForm}>
          <BuilderField
            path="definition.title"
            type="string"
            onChange={(newValue) => {
              if (!isInferredInputOverride) {
                setFieldValue("key", sluggify(newValue || ""), true);
              }
            }}
            label={formatMessage({ id: "connectorBuilder.inputModal.inputName" })}
            tooltip={formatMessage({ id: "connectorBuilder.inputModal.inputNameTooltip" })}
          />
          <BuilderField
            path="key"
            type="string"
            readOnly
            label={formatMessage({ id: "connectorBuilder.inputModal.fieldId" })}
            tooltip={formatMessage(
              { id: "connectorBuilder.inputModal.fieldIdTooltip" },
              {
                syntaxExample: `{{config['${values.key || "my_input"}']}}`,
              }
            )}
          />
          <BuilderField
            path="definition.description"
            optional
            type="string"
            label={formatMessage({ id: "connectorBuilder.inputModal.description" })}
            tooltip={formatMessage({ id: "connectorBuilder.inputModal.descriptionTooltip" })}
          />
          {values.type !== "unknown" && !isInferredInputOverride ? (
            <>
              <BuilderField
                path="type"
                type="enum"
                options={["string", "number", "integer", "array", "boolean", "enum"]}
                onChange={() => {
                  setFieldValue("definition.default", undefined);
                }}
                label={formatMessage({ id: "connectorBuilder.inputModal.type" })}
                tooltip={formatMessage({ id: "connectorBuilder.inputModal.typeTooltip" })}
              />
              {values.type === "enum" && (
                <BuilderField
                  path="definition.enum"
                  type="array"
                  optional
                  label={formatMessage({ id: "connectorBuilder.inputModal.enum" })}
                  tooltip={formatMessage({ id: "connectorBuilder.inputModal.enumTooltip" })}
                />
              )}
              <BuilderField
                path="definition.airbyte_secret"
                type="boolean"
                optional
                label={formatMessage({ id: "connectorBuilder.inputModal.secret" })}
                tooltip={formatMessage({ id: "connectorBuilder.inputModal.secretTooltip" })}
              />
              <BuilderField
                path="required"
                type="boolean"
                optional
                label={formatMessage({ id: "connectorBuilder.inputModal.required" })}
                tooltip={formatMessage({ id: "connectorBuilder.inputModal.requiredTooltip" })}
              />
              <BuilderField
                path="showDefaultValueField"
                type="boolean"
                optional
                label={formatMessage({ id: "connectorBuilder.inputModal.showDefaultValueField" })}
                tooltip={formatMessage({ id: "connectorBuilder.inputModal.showDefaultValueFieldTooltip" })}
              />
              {values.showDefaultValueField && (
                <BuilderField
                  path="definition.default"
                  type={values.type}
                  options={(values.definition.enum || []) as string[]}
                  optional
                  label={formatMessage({ id: "connectorBuilder.inputModal.default" })}
                />
              )}
              <BuilderField
                path="definition.placeholder"
                type="string"
                optional
                label={formatMessage({ id: "connectorBuilder.inputModal.placeholder" })}
                tooltip={formatMessage({ id: "connectorBuilder.inputModal.placeholderTooltip" })}
              />
            </>
          ) : (
            <InfoBox>
              {isInferredInputOverride ? (
                <FormattedMessage id="connectorBuilder.inputModal.inferredInputMessage" />
              ) : (
                <FormattedMessage id="connectorBuilder.inputModal.unsupportedInput" />
              )}
            </InfoBox>
          )}
        </ModalBody>
        <ModalFooter>
          {!inputInEditing.isNew && !inputInEditing.isInferredInputOverride && (
            <div className={styles.deleteButtonContainer}>
              <Button variant="danger" type="button" onClick={onDelete}>
                <FormattedMessage id="form.delete" />
              </Button>
            </div>
          )}
          <Button variant="secondary" type="reset" onClick={onClose}>
            <FormattedMessage id="form.cancel" />
          </Button>
          <Button type="submit" disabled={!isValid}>
            <FormattedMessage id={inputInEditing.isNew ? "form.create" : "form.saveChanges"} />
          </Button>
        </ModalFooter>
      </Form>
    </Modal>
  );
};

const InputItem = ({
  input,
  setInputInEditing,
  isInferredInput,
}: {
  input: BuilderFormInput;
  setInputInEditing: (inputInEditing: InputInEditing) => void;
  isInferredInput: boolean;
}): JSX.Element => {
  return (
    <li className={styles.listItem} key={input.key}>
      <div className={styles.itemLabel}>{input.definition.title || input.key}</div>
      <Button
        className={styles.itemButton}
        size="sm"
        variant="secondary"
        aria-label="Edit"
        onClick={() => {
          setInputInEditing(formInputToInputInEditing(input, isInferredInput));
        }}
      >
        <FontAwesomeIcon className={styles.icon} icon={faGear} />
      </Button>
    </li>
  );
};
