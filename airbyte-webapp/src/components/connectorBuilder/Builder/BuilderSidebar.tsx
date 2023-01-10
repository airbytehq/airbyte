import { faSliders, faUser } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import { useFormikContext } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import Indicator from "components/Indicator";
import { Button } from "components/ui/Button";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { BuilderView, useConnectorBuilderFormState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { DownloadYamlButton } from "../DownloadYamlButton";
import { BuilderFormValues, DEFAULT_BUILDER_FORM_VALUES, getInferredInputs } from "../types";
import { useBuilderErrors } from "../useBuilderErrors";
import { AddStreamButton } from "./AddStreamButton";
import styles from "./BuilderSidebar.module.scss";
import { UiYamlToggleButton } from "./UiYamlToggleButton";

interface ViewSelectButtonProps {
  className?: string;
  selected: boolean;
  showErrorIndicator: boolean;
  onClick: () => void;
}

const ViewSelectButton: React.FC<React.PropsWithChildren<ViewSelectButtonProps>> = ({
  children,
  className,
  selected,
  showErrorIndicator,
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
      <div className={styles.viewLabel}>{children}</div>
      {showErrorIndicator && <Indicator className={styles.errorIndicator} />}
    </button>
  );
};

interface BuilderSidebarProps {
  className?: string;
  toggleYamlEditor: () => void;
}

export const BuilderSidebar: React.FC<BuilderSidebarProps> = React.memo(({ className, toggleYamlEditor }) => {
  const { formatMessage } = useIntl();
  const { hasErrors } = useBuilderErrors();
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { yamlManifest, selectedView, setSelectedView } = useConnectorBuilderFormState();
  const { values, setValues } = useFormikContext<BuilderFormValues>();
  const handleResetForm = () => {
    openConfirmationModal({
      text: "connectorBuilder.resetModal.text",
      title: "connectorBuilder.resetModal.title",
      submitButtonText: "connectorBuilder.resetModal.submitButton",
      onSubmit: () => {
        setValues(DEFAULT_BUILDER_FORM_VALUES);
        setSelectedView("global");
        closeConfirmationModal();
      },
    });
  };
  const handleViewSelect = (selectedView: BuilderView) => {
    setSelectedView(selectedView);
  };

  return (
    <div className={classnames(className, styles.container)}>
      <UiYamlToggleButton yamlSelected={false} onClick={toggleYamlEditor} />

      {/* TODO: replace with uploaded img when that functionality is added */}
      <img
        className={styles.connectorImg}
        src="/logo.png"
        alt={formatMessage({ id: "connectorBuilder.connectorImgAlt" })}
      />

      <div className={styles.connectorName}>
        <Heading as="h2" size="sm" className={styles.connectorNameText}>
          {values.global?.connectorName}
        </Heading>
      </div>

      <ViewSelectButton
        className={styles.globalConfigButton}
        selected={selectedView === "global"}
        showErrorIndicator={hasErrors(true, ["global"])}
        onClick={() => handleViewSelect("global")}
      >
        <FontAwesomeIcon icon={faSliders} />
        <FormattedMessage id="connectorBuilder.globalConfiguration" />
      </ViewSelectButton>

      <ViewSelectButton
        showErrorIndicator={false}
        className={styles.globalConfigButton}
        selected={selectedView === "inputs"}
        onClick={() => handleViewSelect("inputs")}
      >
        <FontAwesomeIcon icon={faUser} />
        <FormattedMessage
          id="connectorBuilder.userInputs"
          values={{
            number: values.inputs.length + getInferredInputs(values.global, values.inferredInputOverrides).length,
          }}
        />
      </ViewSelectButton>

      <div className={styles.streamsHeader}>
        <Text className={styles.streamsHeading} size="xs" bold>
          <FormattedMessage id="connectorBuilder.streamsHeading" values={{ number: values.streams.length }} />
        </Text>

        <AddStreamButton onAddStream={(addedStreamNum) => handleViewSelect(addedStreamNum)} />
      </div>

      <div className={styles.streamList}>
        {values.streams.map(({ name }, num) => (
          <ViewSelectButton
            key={num}
            selected={selectedView === num}
            showErrorIndicator={hasErrors(true, [num])}
            onClick={() => handleViewSelect(num)}
          >
            {name && name.trim() ? (
              <Text className={styles.streamViewText}>{name}</Text>
            ) : (
              <Text className={styles.emptyStreamViewText}>
                <FormattedMessage id="connectorBuilder.emptyName" />
              </Text>
            )}
          </ViewSelectButton>
        ))}
      </div>

      <DownloadYamlButton className={styles.downloadButton} yamlIsValid yaml={yamlManifest} />
      <Button className={styles.resetButton} full variant="clear" onClick={() => handleResetForm()}>
        <FormattedMessage id="connectorBuilder.resetAll" />
      </Button>
    </div>
  );
});
