import { faSortDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Listbox } from "@headlessui/react";
import classNames from "classnames";

import { Text } from "components/ui/Text";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { Heading } from "../ui/Heading";
import styles from "./StreamSelector.module.scss";

export const StreamSelector: React.FC = () => {
  const { streams, selectedStream, setSelectedStream } = useConnectorBuilderState();

  return (
    <Listbox value={selectedStream.name} onChange={setSelectedStream}>
      <Listbox.Button className={classNames(styles.button, styles.centered)}>
        <Heading className={styles.capitalized} as="h1" size="sm">
          {selectedStream.name}
        </Heading>
        <FontAwesomeIcon className={styles.arrow} icon={faSortDown} />
      </Listbox.Button>
      {/* wrap in div to make `position: absolute` on Listbox.Options result in correct vertical positioning */}
      <div>
        <Listbox.Options className={classNames(styles.optionsMenu, styles.centered)}>
          {streams.map(({ name: streamName }) => (
            <Listbox.Option key={streamName} value={streamName} className={styles.option}>
              {({ active }) => (
                <div className={classNames(styles.optionValue, { [styles.active]: active })}>
                  <Text className={styles.capitalized} size="lg">
                    {streamName}
                  </Text>
                </div>
              )}
            </Listbox.Option>
          ))}
        </Listbox.Options>
      </div>
    </Listbox>
  );
};
