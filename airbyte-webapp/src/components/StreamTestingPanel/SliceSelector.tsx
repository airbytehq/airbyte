import { faAngleDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { ListBox, ListBoxControlButtonProps } from "components/ui/ListBox";
import { Text } from "components/ui/Text";

import { StreamReadSlicesItem } from "core/request/ConnectorBuilderClient";

import styles from "./SliceSelector.module.scss";

interface SliceSelectorProps {
  className?: string;
  slices: StreamReadSlicesItem[];
  selectedSliceIndex: number;
  onSelect: (sliceIndex: number) => void;
}

function getSliceLabel(slice: StreamReadSlicesItem, sliceIndex: number) {
  const fallback = `Slice ${sliceIndex}`;

  const sliceDescriptor = slice.sliceDescriptor;

  if (!sliceDescriptor) {
    return fallback;
  }

  const listItem = sliceDescriptor.listItem;
  const startDatetime = sliceDescriptor.startDatetime;

  if (!listItem && !startDatetime) {
    return fallback;
  }

  return [listItem, startDatetime].filter(Boolean).join(" | ");
}

const ControlButton: React.FC<ListBoxControlButtonProps<number>> = ({ selectedOption }) => {
  return (
    <>
      <Text size="md">{selectedOption.label}</Text>
      <FontAwesomeIcon className={styles.arrow} icon={faAngleDown} />
    </>
  );
};

export const SliceSelector: React.FC<SliceSelectorProps> = ({ className, slices, selectedSliceIndex, onSelect }) => {
  const options = slices.map((slice, index) => {
    return { label: getSliceLabel(slice, index), value: index };
  });

  return (
    <ListBox
      className={className}
      options={options}
      selectedValue={selectedSliceIndex}
      onSelect={(selected) => onSelect(selected)}
      buttonClassName={styles.button}
      controlButton={ControlButton}
    />
  );
};
