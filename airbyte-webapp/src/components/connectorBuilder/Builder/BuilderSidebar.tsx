import classnames from "classnames";
import { useField, useFormikContext } from "formik";

import { Heading } from "components/ui/Heading";

import {
  DEFAULT_BUILDER_FORM_VALUES,
  useConnectorBuilderState,
} from "services/connectorBuilder/ConnectorBuilderStateService";

import { DownloadYamlButton } from "../YamlEditor/DownloadYamlButton";
import { AddStreamButton } from "./AddStreamButton";
import styles from "./BuilderSidebar.module.scss";
import { UiYamlToggleButton } from "./UiYamlToggleButton";

export type BuilderView = "global" | number;

interface StreamSelectButtonProps {
  streamPath: string;
  onClick: () => void;
}

const StreamSelectButton: React.FC<StreamSelectButtonProps> = ({ streamPath, onClick }) => {
  const streamNamePath = `${streamPath}.name`;
  console.log("streamNamePath", streamNamePath);
  const [field] = useField(streamNamePath);
  console.log("field.value", field.value);

  return <button onClick={onClick}>{field.value}</button>;
};

interface BuilderSidebarProps {
  className?: string;
  toggleYamlEditor: () => void;
  numStreams: number;
  onViewSelect: (selected: BuilderView) => void;
}

export const BuilderSidebar: React.FC<BuilderSidebarProps> = ({
  className,
  toggleYamlEditor,
  numStreams,
  onViewSelect,
}) => {
  const { yamlManifest } = useConnectorBuilderState();
  const { setValues } = useFormikContext();
  const handleResetForm = () => {
    setValues(DEFAULT_BUILDER_FORM_VALUES);
    onViewSelect("global");
  };

  console.log("numStreams", numStreams);

  return (
    <div className={classnames(className, styles.container)}>
      <UiYamlToggleButton className={styles.yamlToggle} yamlSelected={false} onClick={toggleYamlEditor} />
      <img className={styles.connectorImg} src="/logo.png" alt="Connector Logo" />
      <Heading as="h2" size="sm" className={styles.connectorName}>
        Connector Name
      </Heading>
      <button onClick={() => handleResetForm()}>Reset</button>
      <button onClick={() => onViewSelect("global")}>Global Configuration</button>

      <Heading as="h3" size="sm">
        Streams
      </Heading>

      <AddStreamButton numStreams={numStreams} />

      {Array.from(Array(numStreams).keys()).map((streamNum) => {
        const streamPath = `streams[${streamNum}]`;
        return <StreamSelectButton key={streamPath} streamPath={streamPath} onClick={() => onViewSelect(streamNum)} />;
      })}

      <DownloadYamlButton className={styles.downloadButton} yamlIsValid yaml={yamlManifest} />
    </div>
  );
};
