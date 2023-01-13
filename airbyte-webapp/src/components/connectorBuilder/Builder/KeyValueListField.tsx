import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useField } from "formik";
import { FormattedMessage } from "react-intl";

import GroupControls from "components/GroupControls";
import { ControlLabels } from "components/LabeledControl";
import { Button } from "components/ui/Button";
import { Input } from "components/ui/Input";
import { Text } from "components/ui/Text";

import styles from "./KeyValueListField.module.scss";

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
        <Input value={keyValue[0]} onChange={(e) => onChange([e.target.value, keyValue[1]])} />
      </div>
      <div className={styles.labeledInput}>
        <Text className={styles.kvLabel}>
          <FormattedMessage id="connectorBuilder.value" />
        </Text>
        <Input value={keyValue[1]} onChange={(e) => onChange([keyValue[0], e.target.value])} />
      </div>
      <button type="button" className={styles.removeButton} onClick={onRemove}>
        <FontAwesomeIcon icon={faXmark} size="1x" />
      </button>
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

  return (
    <GroupControls label={<ControlLabels label={label} infoTooltipContent={tooltip} />}>
      {keyValueList.map((keyValue, keyValueIndex) => (
        <KeyValueInput
          key={keyValueIndex}
          keyValue={keyValue}
          onChange={(newKeyValue) => {
            const updatedList = keyValueList.map((entry, index) => (index === keyValueIndex ? newKeyValue : entry));
            setKeyValueList(updatedList);
          }}
          onRemove={() => {
            const updatedList = keyValueList.filter((_, index) => index !== keyValueIndex);
            setKeyValueList(updatedList);
          }}
        />
      ))}
      <div>
        <Button variant="secondary" onClick={() => setKeyValueList([...keyValueList, ["", ""]])}>
          <FormattedMessage id="connectorBuilder.addKeyValue" />
        </Button>
      </div>
    </GroupControls>
  );
};
