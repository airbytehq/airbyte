import { faSortDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import capitalize from "lodash/capitalize";

import { Heading } from "components/ui/Heading";
import { ListBox, ListBoxControlButtonProps } from "components/ui/ListBox";

import { StreamsListReadStreamsItem } from "core/request/ConnectorBuilderClient";
import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./StreamSelector.module.scss";

interface StreamSelectorProps {
  className?: string;
  streams: StreamsListReadStreamsItem[];
  selectedStream: StreamsListReadStreamsItem;
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

export const StreamSelector: React.FC<StreamSelectorProps> = ({ className, streams, selectedStream }) => {
  const { selectedView, setSelectedView, setSelectedStream } = useConnectorBuilderState();
  const options = streams.map((stream) => {
    return { label: capitalize(stream.name), value: stream.name };
  });

  const handleStreamSelect = (selectedStreamName: string) => {
    setSelectedStream(selectedStreamName);

    if (selectedView !== "global") {
      const selectedStreamIndex = streams.findIndex((stream) => stream.name === selectedStreamName);
      if (selectedStreamIndex >= 0) {
        setSelectedView(selectedStreamIndex);
      }
    }
  };

  return (
    <ListBox
      className={classNames(className, styles.container)}
      options={options}
      selectedValue={selectedStream.name}
      onSelect={handleStreamSelect}
      buttonClassName={styles.button}
      controlButton={ControlButton}
    />
  );
};
