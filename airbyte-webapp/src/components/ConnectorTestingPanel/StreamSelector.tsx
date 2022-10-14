import { DropDown, DropDownOptionDataItem } from "components/ui/DropDown";

import styles from "./StreamSelector.module.scss";

interface StreamSelectorProps {
  streams: string[];
  selectedStream: string;
  onSelect: (stream: string) => void;
}

export const StreamSelector: React.FC<StreamSelectorProps> = ({ streams, selectedStream, onSelect }) => {
  const streamOptions = streams.map((streamName) => {
    return { label: streamName, value: streamName };
  });

  const handleSelection = (selection: DropDownOptionDataItem) => {
    onSelect(selection.value);
  };

  return (
    <DropDown
      className={styles.streamSelector}
      value={selectedStream}
      options={streamOptions}
      onChange={handleSelection}
    />
  );
};
