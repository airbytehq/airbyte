import { faRotateLeft } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import { useField, useFormikContext } from "formik";

import { Button } from "components/ui/Button";
import { Heading } from "components/ui/Heading";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
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
  streamNum: number;
  onSelectStream: (streamNum: number, streamName: string) => void;
}

const StreamSelectButton: React.FC<StreamSelectButtonProps> = ({ streamNum, onSelectStream }) => {
  const streamNamePath = `streams[${streamNum}].name`;
  const [field] = useField(streamNamePath);

  return <button onClick={() => onSelectStream(streamNum, field.value)}>{field.value}</button>;
};

interface BuilderSidebarProps {
  className?: string;
  toggleYamlEditor: () => void;
  numStreams: number;
  onViewSelect: (selected: BuilderView, streamName?: string) => void;
}

export const BuilderSidebar: React.FC<BuilderSidebarProps> = ({
  className,
  toggleYamlEditor,
  numStreams,
  onViewSelect,
}) => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { yamlManifest } = useConnectorBuilderState();
  const { setValues } = useFormikContext();
  const handleResetForm = () => {
    openConfirmationModal({
      text: "connectorBuilder.resetModal.text",
      title: "connectorBuilder.resetModal.title",
      submitButtonText: "connectorBuilder.resetModal.submitButton",
      onSubmit: () => {
        setValues(DEFAULT_BUILDER_FORM_VALUES);
        onViewSelect("global");
        closeConfirmationModal();
      },
    });
  };

  console.log("numStreams", numStreams);

  return (
    <div className={classnames(className, styles.container)}>
      <UiYamlToggleButton className={styles.yamlToggle} yamlSelected={false} onClick={toggleYamlEditor} />
      <img className={styles.connectorImg} src="/logo.png" alt="Connector Logo" />
      <Heading as="h2" size="sm" className={styles.connectorName}>
        Connector Name
      </Heading>
      <button onClick={() => onViewSelect("global")}>Global Configuration</button>

      <Heading as="h3" size="sm">
        Streams
      </Heading>

      <AddStreamButton
        numStreams={numStreams}
        onAddStream={(addedStreamNum, addedStreamName) => onViewSelect(addedStreamNum, addedStreamName)}
      />

      {Array.from(Array(numStreams).keys()).map((streamNum) => {
        return <StreamSelectButton key={streamNum} streamNum={streamNum} onSelectStream={onViewSelect} />;
      })}

      <DownloadYamlButton className={styles.downloadButton} yamlIsValid yaml={yamlManifest} />
      <Button
        className={styles.resetButton}
        variant="danger"
        onClick={() => handleResetForm()}
        icon={<FontAwesomeIcon icon={faRotateLeft} />}
      >
        Reset Builder
      </Button>
    </div>
  );
};
