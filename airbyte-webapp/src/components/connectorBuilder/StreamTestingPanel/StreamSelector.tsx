import classNames from "classnames";
import capitalize from "lodash/capitalize";
import { useIntl } from "react-intl";

import { Heading } from "components/ui/Heading";
import { ListBox, ListBoxControlButtonProps } from "components/ui/ListBox";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { ReactComponent as CaretDownIcon } from "../../ui/ListBox/CaretDownIcon.svg";
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
      <CaretDownIcon className={styles.arrow} />
    </>
  );
};

export const StreamSelector: React.FC<StreamSelectorProps> = ({ className }) => {
  const { formatMessage } = useIntl();
  const { streams, selectedView, testStreamIndex, setSelectedView, setTestStreamIndex } = useConnectorBuilderState();
  const options = streams.map((stream) => {
    const label =
      stream.name && stream.name.trim() ? capitalize(stream.name) : formatMessage({ id: "connectorBuilder.emptyName" });
    return { label, value: stream.name };
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
