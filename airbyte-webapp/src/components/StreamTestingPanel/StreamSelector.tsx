import { faSortDown, faWarning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { capitalize } from "lodash";
import { FormattedMessage } from "react-intl";

import { Heading } from "components/ui/Heading";
import { ListBox, ListBoxControlButtonProps } from "components/ui/ListBox";
import { Text } from "components/ui/Text";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./StreamSelector.module.scss";

interface StreamSelectorProps {
  className?: string;
}

const ControlButton: React.FC<ListBoxControlButtonProps<string>> = ({ selectedOption }) => {
  return (
    <>
      <Heading as="h1" size="sm">
        {selectedOption.label}
      </Heading>
      <FontAwesomeIcon className={styles.arrow} icon={faSortDown} />
    </>
  );
};

export const StreamSelector: React.FC<StreamSelectorProps> = ({ className }) => {
  const { streams, selectedStream, setSelectedStream } = useConnectorBuilderState();
  const options = streams.map((stream) => {
    return { label: capitalize(stream.name), value: stream.name };
  });

  return (
    <div className={classNames(className, styles.centered)}>
      {streams.length > 0 && selectedStream !== undefined ? (
        <ListBox
          options={options}
          selectedValue={selectedStream.name}
          onSelect={setSelectedStream}
          buttonClassName={styles.button}
          controlButton={ControlButton}
        />
      ) : (
        <div className={styles.noStreamsContainer}>
          <FontAwesomeIcon icon={faWarning} className={styles.noStreamsIcon} size="lg" />
          <Text className={styles.noStreamsText} size="lg">
            <FormattedMessage id="connectorBuilder.noStreamsDetected" />
          </Text>
        </div>
      )}
    </div>
  );
};
