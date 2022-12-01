import classnames from "classnames";

import { Heading } from "components/ui/Heading";

import styles from "./BuilderSidebar.module.scss";
import { UiYamlToggleButton } from "./UiYamlToggleButton";

interface BuilderSidebarProps {
  className?: string;
  toggleYamlEditor: () => void;
}

export const BuilderSidebar: React.FC<BuilderSidebarProps> = ({ className, toggleYamlEditor }) => {
  return (
    <div className={classnames(className, styles.container)}>
      <UiYamlToggleButton className={styles.yamlToggle} yamlSelected={false} onClick={toggleYamlEditor} />
      <img className={styles.connectorImg} src="/logo.png" alt="Connector Logo" />
      <Heading as="h2" size="sm" className={styles.connectorName}>
        Connector Name
      </Heading>
    </div>
  );
};
