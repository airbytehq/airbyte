import { faWarning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { FormattedMessage } from "react-intl";

import { RotateIcon } from "components/icons/RotateIcon";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { ConfigMenu } from "./ConfigMenu";
import styles from "./TestControls.module.scss";

interface TestControlsProps {
  onClickTest: () => void;
  className?: string;
}

export const TestControls: React.FC<TestControlsProps> = ({ onClickTest, className }) => {
  const { selectedStream, yamlIsValid } = useConnectorBuilderState();

  const testButton = (
    <Button
      className={styles.testButton}
      size="sm"
      onClick={onClickTest}
      disabled={!yamlIsValid}
      icon={
        yamlIsValid ? (
          <div>
            <RotateIcon width={styles.testIconHeight} height={styles.testIconHeight} />
          </div>
        ) : (
          <FontAwesomeIcon icon={faWarning} />
        )
      }
    >
      <Text className={styles.testButtonText} size="sm" bold>
        <FormattedMessage id="connectorBuilder.testButton" />
      </Text>
    </Button>
  );

  return (
    <div className={classNames(className, styles.container)}>
      <ConfigMenu />
      <div className={styles.urlDisplay}>
        <Tooltip control={<Text size="lg">{selectedStream.url}</Text>}>{selectedStream.url}</Tooltip>
      </div>
      {yamlIsValid ? (
        testButton
      ) : (
        <Tooltip control={testButton}>
          <FormattedMessage id="connectorBuilder.invalidYamlTest" />
        </Tooltip>
      )}
    </div>
  );
};
