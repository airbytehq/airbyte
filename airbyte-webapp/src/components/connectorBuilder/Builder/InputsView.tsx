import { Form, Formik, useField } from "formik";
import { JSONSchema7 } from "json-schema";
import { useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { Modal, ModalBody, ModalFooter } from "components/ui/Modal";

import { FormikPatch } from "core/form/FormikPatch";

import { BuilderFormValues } from "../types";
import { BuilderField } from "./BuilderField";

interface InputInEditing {
  key: string;
  definition: JSONSchema7;
  required: boolean;
  isNew?: boolean;
  showDefaultValueField?: boolean;
}

export const InputsView: React.FC = () => {
  const { formatMessage } = useIntl();
  const [inputs, , helpers] = useField<BuilderFormValues["inputs"]>("inputs");
  const [inputInEditing, setInputInEditing] = useState<InputInEditing | undefined>(undefined);
  const usedKeys = useMemo(() => inputs.value.map((input) => input.key), [inputs.value]);
  const inputInEditValidation = useMemo(
    () =>
      yup.object().shape({
        // make sure key can only occur once
        key: yup
          .string()
          .required("form.empty.error")
          .notOneOf(inputInEditing?.isNew ? usedKeys : usedKeys.filter((key) => key !== inputInEditing?.key)),
        required: yup.bool(),
        definition: yup.object().shape({
          title: yup.string().required("form.empty.error"),
        }),
      }),
    [inputInEditing?.isNew, inputInEditing?.key, usedKeys]
  );
  return (
    <>
      <Card>
        <ol>
          {inputs.value.map(({ key, definition }) => (
            <li key={key}>
              <button
                onClick={() => {
                  setInputInEditing({
                    key,
                    definition,
                    required: false,
                    isNew: false,
                    showDefaultValueField: Boolean(definition.default),
                  });
                }}
              >
                {definition.title || key}
              </button>
            </li>
          ))}
        </ol>
      </Card>
      <Button
        onClick={() => {
          setInputInEditing({
            key: "",
            definition: {
              type: "string",
            },
            required: false,
            isNew: true,
            showDefaultValueField: false,
          });
        }}
      >
        <FormattedMessage id="connectorBuilder.addInputButton" />
      </Button>
      {inputInEditing && (
        <Formik
          initialValues={inputInEditing}
          validationSchema={inputInEditValidation}
          onSubmit={({ isNew, ...values }: InputInEditing) => {
            helpers.setValue(
              inputInEditing.isNew
                ? [...inputs.value, values]
                : inputs.value.map((input) => (input.key === inputInEditing.key ? values : input))
            );
            setInputInEditing(undefined);
          }}
        >
          {({ values }) => (
            <>
              <FormikPatch />
              <Modal
                size="sm"
                title={<FormattedMessage id="connectorBuilder.inputModal.title" />}
                onClose={() => {
                  setInputInEditing(undefined);
                }}
              >
                <Form>
                  <ModalBody>
                    <BuilderField
                      path="definition.title"
                      type="text"
                      label={formatMessage({ id: "connectorBuilder.inputModal.inputName" })}
                      tooltip={formatMessage({ id: "connectorBuilder.inputModal.inputNameTooltip" })}
                    />
                    <BuilderField
                      path="key"
                      type="text"
                      label={formatMessage({ id: "connectorBuilder.inputModal.key" })}
                      tooltip={formatMessage({ id: "connectorBuilder.inputModal.keyTooltip" })}
                    />
                    <BuilderField
                      path="definition.description"
                      optional
                      type="text"
                      label={formatMessage({ id: "connectorBuilder.inputModal.description" })}
                      tooltip={formatMessage({ id: "connectorBuilder.inputModal.descriptionTooltip" })}
                    />
                    <BuilderField
                      path="definition.type"
                      type="enum"
                      options={["string", "number", "integer"]}
                      label={formatMessage({ id: "connectorBuilder.inputModal.type" })}
                      tooltip={formatMessage({ id: "connectorBuilder.inputModal.typeTooltip" })}
                    />
                    <BuilderField
                      path="definition.airbyte_hidden"
                      type="boolean"
                      optional
                      label={formatMessage({ id: "connectorBuilder.inputModal.secret" })}
                      tooltip={formatMessage({ id: "connectorBuilder.inputModal.secretTooltip" })}
                    />
                    <BuilderField
                      path="definition.required"
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
                        type={values.definition.type === "string" ? "text" : "number"}
                        optional
                        label={formatMessage({ id: "connectorBuilder.inputModal.showDefaultValueField" })}
                        tooltip={formatMessage({ id: "connectorBuilder.inputModal.showDefaultValueFieldTooltip" })}
                      />
                    )}
                    <BuilderField
                      path="definition.placeholder"
                      type="text"
                      optional
                      label={formatMessage({ id: "connectorBuilder.inputModal.placeholder" })}
                      tooltip={formatMessage({ id: "connectorBuilder.inputModal.placeholderTooltip" })}
                    />
                  </ModalBody>
                  <ModalFooter>
                    <Button
                      variant="danger"
                      type="button"
                      onClick={() => {
                        helpers.setValue(inputs.value.filter((input) => input.key !== inputInEditing.key));
                        setInputInEditing(undefined);
                      }}
                    >
                      <FormattedMessage id="form.delete" />
                    </Button>
                    <Button
                      variant="secondary"
                      type="reset"
                      onClick={() => {
                        setInputInEditing(undefined);
                      }}
                    >
                      <FormattedMessage id="form.cancel" />
                    </Button>
                    <Button type="submit">
                      <FormattedMessage id={inputInEditing.isNew ? "form.create" : "form.saveChanges"} />
                    </Button>
                  </ModalFooter>
                </Form>
              </Modal>
            </>
          )}
        </Formik>
      )}
    </>
  );
  return <>TODO: List all inputs</>;
};
