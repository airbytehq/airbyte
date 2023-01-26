import { faGear, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useFormikContext } from "formik";
import { useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { Text } from "components/ui/Text";

import { BuilderConfigView } from "./BuilderConfigView";
import { InputForm, InputInEditing, newInputInEditing } from "./InputsForm";
import styles from "./InputsView.module.scss";
import { BuilderFormInput, BuilderFormValues, getInferredInputs } from "../types";

const supportedTypes = ["string", "integer", "number", "array", "boolean", "enum", "unknown"] as const;

export const InputsView: React.FC = () => {
  const { formatMessage } = useIntl();
  const { values } = useFormikContext<BuilderFormValues>();
  const [inputInEditing, setInputInEditing] = useState<InputInEditing | undefined>(undefined);
  const inferredInputs = useMemo(
    () => getInferredInputs(values.global, values.inferredInputOverrides),
    [values.global, values.inferredInputOverrides]
  );

  return (
    <BuilderConfigView heading={formatMessage({ id: "connectorBuilder.inputsTitle" })}>
      <Text centered className={styles.inputsDescription}>
        <FormattedMessage id="connectorBuilder.inputsDescription" />
      </Text>
      {(values.inputs.length > 0 || inferredInputs.length > 0) && (
        <Card withPadding className={styles.inputsCard}>
          <ol className={styles.list}>
            {inferredInputs.map((input) => (
              <InputItem key={input.key} input={input} setInputInEditing={setInputInEditing} isInferredInput />
            ))}
            {values.inputs.map((input) => (
              <InputItem key={input.key} input={input} setInputInEditing={setInputInEditing} isInferredInput={false} />
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
        <InputForm
          inputInEditing={inputInEditing}
          onClose={() => {
            setInputInEditing(undefined);
          }}
        />
      )}
    </BuilderConfigView>
  );
};

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
