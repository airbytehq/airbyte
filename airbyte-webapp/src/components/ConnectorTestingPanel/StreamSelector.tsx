import { faSortDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Listbox } from "@headlessui/react";
import classNames from "classnames";

import { Text } from "components/ui/Text";

import styles from "./StreamSelector.module.scss";
interface StreamSelectorProps {
  streams: string[];
  selectedStream: string;
  onSelect: (stream: string) => void;
}

export const StreamSelector: React.FC<StreamSelectorProps> = ({ streams, selectedStream, onSelect }) => {
  return (
    <Listbox value={selectedStream} onChange={onSelect}>
      <Listbox.Button className={classNames(styles.button, styles.centered)}>
        <Text as="h1" size="sm">
          {selectedStream}
        </Text>
        <FontAwesomeIcon className={styles.arrow} icon={faSortDown} />
      </Listbox.Button>
      <Listbox.Options className={classNames(styles.optionsMenu, styles.centered)}>
        {streams.map((stream) => (
          <Listbox.Option key={stream} value={stream} className={styles.option}>
            {({ active }) => (
              <div className={classNames(styles.optionValue, { [styles.active]: active })}>
                <Text size="lg">{stream}</Text>
              </div>
            )}
          </Listbox.Option>
        ))}
      </Listbox.Options>
    </Listbox>
  );
};
