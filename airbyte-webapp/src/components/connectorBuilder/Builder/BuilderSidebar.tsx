import classnames from "classnames";

import { Heading } from "components/ui/Heading";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { DownloadYamlButton } from "../YamlEditor/DownloadYamlButton";
import styles from "./BuilderSidebar.module.scss";
import { UiYamlToggleButton } from "./UiYamlToggleButton";

interface BuilderSidebarProps {
  className?: string;
  toggleYamlEditor: () => void;
}

export const BuilderSidebar: React.FC<BuilderSidebarProps> = ({ className, toggleYamlEditor }) => {
  const { yamlManifest } = useConnectorBuilderState();

  return (
    <div className={classnames(className, styles.container)}>
      <UiYamlToggleButton className={styles.yamlToggle} yamlSelected={false} onClick={toggleYamlEditor} />
      <img className={styles.connectorImg} src="/logo.png" alt="Connector Logo" />
      <Heading as="h2" size="sm" className={styles.connectorName}>
        Connector Name
      </Heading>
      <DownloadYamlButton className={styles.downloadButton} yamlIsValid yaml={yamlManifest} />
    </div>
  );
};
