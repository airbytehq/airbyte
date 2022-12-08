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

interface ViewSelectButtonProps {
  className?: string;
  selected: boolean;
  onClick: () => void;
}

const ViewSelectButton: React.FC<React.PropsWithChildren<ViewSelectButtonProps>> = ({
  children,
  className,
  selected,
  onClick,
}) => {
  return (
    <button
      className={classnames(className, styles.viewButton, {
        [styles.selectedViewButton]: selected,
        [styles.unselectedViewButton]: !selected,
      })}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

interface StreamSelectButtonProps {
  streamNum: number;
  onSelectStream: (streamNum: number, streamName: string) => void;
  selected: boolean;
}

const StreamSelectButton: React.FC<StreamSelectButtonProps> = ({ streamNum, onSelectStream, selected }) => {
  const streamPath = `streams[${streamNum}]`;
  const [field] = useField(`${streamPath}.name`);

  return (
    <ViewSelectButton selected={selected} onClick={() => onSelectStream(streamNum, field.value)}>
      {field.value}
    </ViewSelectButton>
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
  const { setValues, setTouched } = useFormikContext();
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

  const [field] = useField("global.connectorName");

  return (
    <div className={classnames(className, styles.container)}>
      <UiYamlToggleButton yamlSelected={false} onClick={toggleYamlEditor} />

      {/* TODO: replace with uploaded img when that functionality is added */}
      <img className={styles.connectorImg} src="/logo.png" alt="Connector Logo" />

      <div className={styles.connectorName}>
        <Heading as="h2" size="sm" className={styles.connectorNameText}>
          {field.value}
        </Heading>
      </div>

      <ViewSelectButton
        className={styles.globalConfigButton}
        selected={selectedView === "global"}
        onClick={() => onViewSelect("global")}
      >
        <FontAwesomeIcon icon={faSliders} />
        <FormattedMessage id="connectorBuilder.globalConfiguration" />
      </ViewSelectButton>

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

      <Button onClick={() => setTouched({}, true)}>Touch</Button>

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
