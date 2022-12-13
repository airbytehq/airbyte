import classnames from "classnames";
import { FormattedMessage } from "react-intl";

import { Text } from "components/ui/Text";

import styles from "./UiYamlToggleButton.module.scss";

interface UiYamlToggleButtonProps {
  className?: string;
  yamlSelected: boolean;
  onClick: () => void;
}

export const UiYamlToggleButton: React.FC<UiYamlToggleButtonProps> = ({ className, yamlSelected, onClick }) => {
  return (
    <button className={classnames(styles.button, className)} onClick={onClick}>
      <Text
        className={classnames(styles.text, {
          [styles.selected]: !yamlSelected,
          [styles.unselected]: yamlSelected,
        })}
        size="xs"
        bold
      >
        <FormattedMessage id="connectorBuilder.uiYamlToggle.ui" />
      </Text>
      <Text
        className={classnames(styles.text, {
          [styles.selected]: yamlSelected,
          [styles.unselected]: !yamlSelected,
        })}
        size="xs"
        bold
      >
        <FormattedMessage id="connectorBuilder.uiYamlToggle.yaml" />
      </Text>
    </button>
  );
};
