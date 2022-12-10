import { faSortDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import capitalize from "lodash/capitalize";

import { Heading } from "components/ui/Heading";
import { ListBox, ListBoxControlButtonProps } from "components/ui/ListBox";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./StreamSelector.module.scss";

interface StreamSelectorProps {
  className?: string;
}

const ControlButton: React.FC<ListBoxControlButtonProps<string>> = ({ selectedOption }) => {
  return (
    <>
      <Heading className={styles.label} as="h1" size="sm">
        {selectedOption.label}
      </Heading>
      <FontAwesomeIcon className={styles.arrow} icon={faSortDown} />
    </>
  );
};

export const StreamSelector: React.FC<StreamSelectorProps> = ({ className }) => {
  const { streams, selectedView, testStreamIndex, setSelectedView, setTestStreamIndex } = useConnectorBuilderState();
  const options = streams.map((stream) => {
    return { label: capitalize(stream.name), value: stream.name };
  });

  const handleStreamSelect = (selectedStreamName: string) => {
    const selectedStreamIndex = streams.findIndex((stream) => selectedStreamName === stream.name);
    if (selectedStreamIndex >= 0) {
      setTestStreamIndex(selectedStreamIndex);

      if (selectedView !== "global" && selectedStreamIndex >= 0) {
        setSelectedView(selectedStreamIndex);
      }
    }
  };

  return (
    <ListBox
      className={classNames(className, styles.container)}
      options={options}
      selectedValue={streams[testStreamIndex]?.name}
      onSelect={handleStreamSelect}
      buttonClassName={styles.button}
      controlButton={ControlButton}
    />
  );
};
