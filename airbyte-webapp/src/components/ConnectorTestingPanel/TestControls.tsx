import { FormattedMessage } from "react-intl";

import { RotateIcon } from "components/icons/RotateIcon";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import styles from "./TestControls.module.scss";

interface TestControlsProps {
  url: string;
  onClickTest: () => void;
}

export const TestControls: React.FC<TestControlsProps> = ({ url, onClickTest }) => {
  return (
    <div className={styles.container}>
      <div className={styles.urlDisplay}>
        <Text size="lg">{url}</Text>
      </div>
      <Button
        className={styles.testButton}
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
