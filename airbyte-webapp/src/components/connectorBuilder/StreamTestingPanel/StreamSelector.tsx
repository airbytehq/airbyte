import classNames from "classnames";
import capitalize from "lodash/capitalize";

import { Heading } from "components/ui/Heading";
import { ListBox, ListBoxControlButtonProps } from "components/ui/ListBox";

import { StreamsListReadStreamsItem } from "core/request/ConnectorBuilderClient";
import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { ReactComponent as CaretDownIcon } from "../../ui/ListBox/CaretDownIcon.svg";
import styles from "./StreamSelector.module.scss";

interface StreamSelectorProps {
  className?: string;
  streams: StreamsListReadStreamsItem[];
  selectedStream: StreamsListReadStreamsItem;
}

const ControlButton: React.FC<ListBoxControlButtonProps<string>> = ({ selectedOption }) => {
  return (
    <>
      <Heading as="h1" size="sm">
        {selectedOption.label}
      </Heading>
      <CaretDownIcon className={styles.arrow} />
    </>
  );
};

export const StreamSelector: React.FC<StreamSelectorProps> = ({ className, streams, selectedStream }) => {
  const { setSelectedStream } = useConnectorBuilderState();
  const options = streams.map((stream) => {
    return { label: capitalize(stream.name), value: stream.name };
  });

  return (
    <ListBox
      className={classNames(className, styles.centered)}
      options={options}
      selectedValue={selectedStream.name}
      onSelect={setSelectedStream}
      buttonClassName={styles.button}
      controlButton={ControlButton}
    />
  );
};
