import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useField } from "formik";
import { FormattedMessage } from "react-intl";

import GroupControls from "components/GroupControls";
import { ControlLabels } from "components/LabeledControl";
import { Button } from "components/ui/Button";
import { Input } from "components/ui/Input";

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
        <FormattedMessage id="connectorBuilder.key" />
        <Input value={keyValue[0]} onChange={(e) => onChange([e.target.value, keyValue[1]])} />
      </div>
      <div className={styles.labeledInput}>
        <FormattedMessage id="connectorBuilder.value" />
        <Input value={keyValue[1]} onChange={(e) => onChange([keyValue[0], e.target.value])} />
      </div>
      <button type="button" onClick={onRemove}>
        <FontAwesomeIcon icon={faXmark} />
      </button>
    </div>
  );
};

interface KeyValueListFieldProps {
  path: string;
  label: string;
  tooltip: string;
  // keyValueList: Array<[string, string]>;
  // setValue: (newValue: Array<[string, string]>) => void;
}

export const KeyValueListField: React.FC<KeyValueListFieldProps> = ({ path, label, tooltip }) => {
  const [{ value: keyValueList }, , { setValue: setKeyValueList }] = useField<Array<[string, string]>>(path);
  // const [keyValues, setKeyValues] = useState<KeyValue[]>(
  //   Object.keys(object).map((key) => {
  //     return { key, value: object[key] };
  //   })
  // );
  console.log(JSON.stringify(keyValueList));

  // useEffect(() => {
  //   const updatedObject = keyValues.reduce((acc, kv) => ({ ...acc, [kv.key]: kv.value }), {});
  //   const updatedObject = Object.fromE;
  //   setValue(updatedObject);
  // }, [keyValues]);

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
            console.log(`Removing index ${keyValueIndex}`);
            console.log(keyValueList);
            const updatedList = keyValueList.filter((_, index) => index !== keyValueIndex);
            console.log(updatedList);
            setKeyValueList(updatedList);
          }}
        />
      ))}
      <Button onClick={() => setKeyValueList([...keyValueList, ["", ""]])}>Add key/value</Button>
    </GroupControls>
  );
};
