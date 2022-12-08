import classnames from "classnames";

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
        UI
      </Text>
      <Text
        className={classnames(styles.text, {
          [styles.selected]: yamlSelected,
          [styles.unselected]: !yamlSelected,
        })}
        size="xs"
        bold
      >
        YAML
      </Text>
    </button>
  );
};
