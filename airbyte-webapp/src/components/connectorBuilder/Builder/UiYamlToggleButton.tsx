import classnames from "classnames";
import { FormattedMessage } from "react-intl";

import { Text } from "components/ui/Text";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

import styles from "./UiYamlToggleButton.module.scss";

interface UiYamlToggleButtonProps {
  className?: string;
  yamlSelected: boolean;
  onClick: () => void;
}

export const UiYamlToggleButton: React.FC<UiYamlToggleButtonProps> = ({ className, yamlSelected, onClick }) => {
  const analyticsService = useAnalyticsService();

  return (
    <button
      className={classnames(styles.button, className)}
      onClick={() => {
        onClick();
        analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.TOGGLE_UI_YAML, {
          actionDescription: "User clicked the UI | YAML toggle button",
          current_view: yamlSelected ? "yaml" : "ui",
          new_view: yamlSelected ? "ui" : "yaml",
        });
      }}
    >
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
