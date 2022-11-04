import classNames from "classnames";
import { FormattedMessage } from "react-intl";

import { RotateIcon } from "components/icons/RotateIcon";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { ConfigMenu } from "./ConfigMenu";
import styles from "./TestControls.module.scss";

interface TestControlsProps {
  onClickTest: () => void;
  className?: string;
}

export const TestControls: React.FC<TestControlsProps> = ({ onClickTest, className }) => {
  const { selectedStream } = useConnectorBuilderState();

  return (
    <div className={classNames(className, styles.container)}>
      <ConfigMenu />
      <div className={styles.urlDisplay}>
        <Text size="lg">{selectedStream.url}</Text>
      </div>
      <Button
        className={styles.testButton}
        size="sm"
        onClick={onClickTest}
        icon={
          <div>
            <RotateIcon width={styles.testIconHeight} height={styles.testIconHeight} />
          </div>
        }
      >
        <Text className={styles.testButtonText} size="sm" bold>
          <FormattedMessage id="connectorBuilder.testButton" />
        </Text>
      </Button>
    </div>
  );
};
