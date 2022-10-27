import { faAngleDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { ListBox } from "components/ui/ListBox";
import { Text } from "components/ui/Text";

import { StreamReadSlicesItem } from "core/request/ConnectorBuilderClient";

import styles from "./SliceSelector.module.scss";

interface SliceSelectorProps {
  className?: string;
  slices: StreamReadSlicesItem[];
  selectedSliceIndex: number;
  onSelect: (sliceIndex: number) => void;
}

export const SliceSelector: React.FC<SliceSelectorProps> = ({ className, slices, selectedSliceIndex, onSelect }) => {
  const sliceIndexes = [...Array.from(slices.keys())].map((index) => index.toString());

  const getSliceLabel = (value: string) => {
    const fallback = `Slice ${value}`;

    if (!sliceIndexes.includes(value)) {
      return fallback;
    }

    const sliceDescriptor = slices[Number(value)].sliceDescriptor;

    if (!sliceDescriptor) {
      return fallback;
    }

    const listItem = sliceDescriptor.listItem;
    const startDatetime = sliceDescriptor.startDatetime;

    if (!listItem && !startDatetime) {
      return fallback;
    }

    return [listItem, startDatetime].filter(Boolean).join(" | ");
  };

  return (
    <ListBox
      className={className}
      values={sliceIndexes}
      selectedValue={selectedSliceIndex.toString()}
      onSelect={(selected) => onSelect(Number(selected))}
      buttonClassName={styles.button}
      buttonContent={(value) => {
        return (
          <>
            <Text size="md">{getSliceLabel(value)}</Text>
            <FontAwesomeIcon className={styles.arrow} icon={faAngleDown} />
          </>
        );
      }}
      optionContent={(value) => {
        return <Text size="md">{getSliceLabel(value)}</Text>;
      }}
    />
  );
};
