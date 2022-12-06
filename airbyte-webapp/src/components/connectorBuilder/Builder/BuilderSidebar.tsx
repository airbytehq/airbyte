import { faRotateLeft, faSliders } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import { useField, useFormikContext } from "formik";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";

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
  selected: boolean;
}

const StreamSelectButton: React.FC<StreamSelectButtonProps> = ({ streamNum, onSelectStream, selected }) => {
  const streamNamePath = `streams[${streamNum}].name`;
  const [field] = useField(streamNamePath);

  return (
    <button
      className={classnames(styles.viewButton, {
        [styles.selectedViewButton]: selected,
        [styles.unselectedViewButton]: !selected,
      })}
      onClick={() => onSelectStream(streamNum, field.value)}
    >
      {field.value}
    </button>
  );
};

interface BuilderSidebarProps {
  className?: string;
  toggleYamlEditor: () => void;
  numStreams: number;
  onViewSelect: (selected: BuilderView, streamName?: string) => void;
  selectedView: BuilderView;
}

export const BuilderSidebar: React.FC<BuilderSidebarProps> = ({
  className,
  toggleYamlEditor,
  numStreams,
  onViewSelect,
  selectedView,
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

  const [field] = useField("connectorName");

  console.log("numStreams", numStreams);

  return (
    <div className={classnames(className, styles.container)}>
      <UiYamlToggleButton yamlSelected={false} onClick={toggleYamlEditor} />
      <img className={styles.connectorImg} src="/logo.png" alt="Connector Logo" />
      <div className={styles.connectorName}>
        <Heading as="h2" size="sm" className={styles.connectorNameText}>
          {field.value}
        </Heading>
      </div>

      <button
        className={classnames(styles.globalConfigButton, styles.viewButton, {
          [styles.selectedViewButton]: selectedView === "global",
          [styles.unselectedViewButton]: selectedView !== "global",
        })}
        onClick={() => onViewSelect("global")}
      >
        <FontAwesomeIcon icon={faSliders} />
        <FormattedMessage id="connectorBuilder.globalConfiguration" />
      </button>

      <div className={styles.streamsHeader}>
        <Text className={styles.streamsHeading} size="xs" bold>
          <FormattedMessage id="connectorBuilder.streamsHeading" values={{ number: numStreams }} />
        </Text>

        <AddStreamButton
          className={styles.addStreamButton}
          numStreams={numStreams}
          onAddStream={(addedStreamNum, addedStreamName) => onViewSelect(addedStreamNum, addedStreamName)}
        />
      </div>

      <div className={styles.streamList}>
        {Array.from(Array(numStreams).keys()).map((streamNum) => {
          return (
            <StreamSelectButton
              key={streamNum}
              streamNum={streamNum}
              onSelectStream={onViewSelect}
              selected={selectedView === streamNum}
            />
          );
        })}
      </div>

      <DownloadYamlButton className={styles.downloadButton} yamlIsValid yaml={yamlManifest} />
      <Button
        className={styles.resetButton}
        variant="secondary"
        onClick={() => handleResetForm()}
        icon={<FontAwesomeIcon icon={faRotateLeft} />}
      >
        Reset Builder
      </Button>
    </div>
  );
};
