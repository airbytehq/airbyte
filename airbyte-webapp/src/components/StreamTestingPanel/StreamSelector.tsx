import { faSortDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { capitalize } from "lodash";

import { ListBox } from "components/ui/ListBox";
import { Text } from "components/ui/Text";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./StreamSelector.module.scss";

interface StreamSelectorProps {
  className?: string;
}

export const StreamSelector: React.FC<StreamSelectorProps> = ({ className }) => {
  const { streams, selectedStream, setSelectedStream } = useConnectorBuilderState();
  const streamNames = streams.map((stream) => capitalize(stream.name));

  return (
    <ListBox
      className={classNames(className, styles.centered)}
      values={streamNames}
      selectedValue={capitalize(selectedStream.name)}
      onSelect={setSelectedStream}
      buttonClassName={styles.button}
      buttonContent={(value) => {
        return (
          <>
            <Text as="h1" size="sm">
              {value}
            </Text>
            <FontAwesomeIcon className={styles.arrow} icon={faSortDown} />
          </>
        );
      }}
    />
  );
};
