import { useField } from "formik";
import React, { useRef } from "react";
import { FormattedMessage } from "react-intl";

import GroupControls from "components/GroupControls";
import { ControlLabels } from "components/LabeledControl";
import { Button } from "components/ui/Button";
import { Input } from "components/ui/Input";
import { Text } from "components/ui/Text";

import { UserInputHelper } from "./BuilderFieldWithInputs";
import styles from "./KeyValueListField.module.scss";
import { RemoveButton } from "./RemoveButton";

interface KeyValueInputProps {
  keyValue: [string, string];
  onChange: (keyValue: [string, string]) => void;
  onRemove: () => void;
}

const KeyValueInput: React.FC<KeyValueInputProps> = ({ keyValue, onChange, onRemove }) => {
  return (
    <div className={styles.inputContainer}>
      <div className={styles.labeledInput}>
        <Text className={styles.kvLabel}>
          <FormattedMessage id="connectorBuilder.key" />
        </Text>
        <Input
          value={keyValue[0]}
          onChange={(e) => onChange([e.target.value, keyValue[1]])}
          adornment={
            <UserInputHelper setValue={(newValue) => onChange([newValue, keyValue[1]])} currentValue={keyValue[0]} />
          }
          className={styles.inputWithHelper}
        />
      </div>
      <div className={styles.labeledInput}>
        <Text className={styles.kvLabel}>
          <FormattedMessage id="connectorBuilder.value" />
        </Text>
        <Input
          value={keyValue[1]}
          onChange={(e) => onChange([keyValue[0], e.target.value])}
          adornment={
            <UserInputHelper setValue={(newValue) => onChange([keyValue[0], newValue])} currentValue={keyValue[1]} />
          }
          className={styles.inputWithHelper}
        />
      </div>
      <RemoveButton onClick={onRemove} />
    </div>
  );
};

interface KeyValueListFieldProps {
  path: string;
  label: string;
  tooltip: string;
}

export const KeyValueListField: React.FC<KeyValueListFieldProps> = ({ path, label, tooltip }) => {
  const [{ value: keyValueList }, , { setValue: setKeyValueList }] = useField<Array<[string, string]>>(path);

  // need to wrap the setter into a ref because it will be a new function on every formik state update
  const setKeyValueListRef = useRef(setKeyValueList);
  setKeyValueListRef.current = setKeyValueList;

  return (
    <KeyValueList label={label} tooltip={tooltip} keyValueList={keyValueList} setKeyValueList={setKeyValueListRef} />
  );
};

const KeyValueList = React.memo(
  ({
    keyValueList,
    setKeyValueList,
    label,
    tooltip,
  }: Omit<KeyValueListFieldProps, "path"> & {
    keyValueList: Array<[string, string]>;
    setKeyValueList: React.MutableRefObject<(val: Array<[string, string]>) => void>;
  }) => {
    return (
      <GroupControls
        label={<ControlLabels label={label} infoTooltipContent={tooltip} />}
        control={
          <Button
            type="button"
            variant="secondary"
            onClick={() => setKeyValueList.current([...keyValueList, ["", ""]])}
          >
            <FormattedMessage id="connectorBuilder.addKeyValue" />
          </Button>
        }
      >
        {keyValueList.map((keyValue, keyValueIndex) => (
          <KeyValueInput
            key={keyValueIndex}
            keyValue={keyValue}
            onChange={(newKeyValue) => {
              const updatedList = keyValueList.map((entry, index) => (index === keyValueIndex ? newKeyValue : entry));
              setKeyValueList.current(updatedList);
            }}
            onRemove={() => {
              const updatedList = keyValueList.filter((_, index) => index !== keyValueIndex);
              setKeyValueList.current(updatedList);
            }}
          />
        ))}
      </GroupControls>
    );
  }
);
