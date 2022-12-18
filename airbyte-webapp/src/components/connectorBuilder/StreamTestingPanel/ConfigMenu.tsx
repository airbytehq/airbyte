import { faClose, faGear } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useLocalStorage } from "react-use";

import { Button } from "components/ui/Button";
import { InfoBox } from "components/ui/InfoBox";
import { Modal, ModalBody } from "components/ui/Modal";
import { Tooltip } from "components/ui/Tooltip";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { ConnectorForm } from "views/Connector/ConnectorForm";

import styles from "./ConfigMenu.module.scss";
import { ConfigMenuErrorBoundaryComponent } from "./ConfigMenuErrorBoundary";

interface ConfigMenuProps {
  className?: string;
}

export const ConfigMenu: React.FC<ConfigMenuProps> = ({ className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { formatMessage } = useIntl();
  const { configString, setConfigString, jsonManifest, editorView, setEditorView } = useConnectorBuilderState();

  const [showInputsWarning, setShowInputsWarning] = useLocalStorage<boolean>("connectorBuilderInputsWarning", true);

  const formValues = useMemo(() => {
    return { connectionConfiguration: JSON.parse(configString) };
  }, [configString]);

  const switchToYaml = () => {
    setEditorView("yaml");
    setIsOpen(false);
  };

  return (
    <>
      <Tooltip
        control={
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setIsOpen(true)}
            disabled={!jsonManifest.spec}
            icon={<FontAwesomeIcon className={styles.icon} icon={faGear} />}
          />
        }
        placement={editorView === "yaml" ? "left" : "top"}
        containerClassName={className}
      >
        {jsonManifest.spec ? (
          <FormattedMessage id="connectorBuilder.inputsTooltip" />
        ) : editorView === "ui" ? (
          <FormattedMessage id="connectorBuilder.inputsNoSpecUITooltip" />
        ) : (
          <FormattedMessage id="connectorBuilder.inputsNoSpecYAMLTooltip" />
        )}
      </Tooltip>
      {isOpen && jsonManifest.spec && (
        <Modal
          size="lg"
          onClose={() => setIsOpen(false)}
          title={<FormattedMessage id="connectorBuilder.configMenuTitle" />}
        >
          <ModalBody>
            <ConfigMenuErrorBoundaryComponent currentView={editorView} closeAndSwitchToYaml={switchToYaml}>
              <>
                {showInputsWarning && (
                  <InfoBox className={styles.warningBox}>
                    <div className={styles.warningBoxContainer}>
                      <div>
                        <FormattedMessage id="connectorBuilder.inputsFormWarning" />
                      </div>
                      <Button
                        onClick={() => {
                          setShowInputsWarning(false);
                        }}
                        variant="clear"
                        icon={<FontAwesomeIcon icon={faClose} />}
                      />
                    </div>
                  </InfoBox>
                )}
                <ConnectorForm
                  formType="source"
                  bodyClassName={styles.formContent}
                  footerClassName={styles.inputFormModalFooter}
                  selectedConnectorDefinitionSpecification={jsonManifest.spec}
                  formValues={formValues}
                  onSubmit={async (values) => {
                    setConfigString(JSON.stringify(values.connectionConfiguration, null, 2) ?? "");
                    setIsOpen(false);
                  }}
                  onCancel={() => {
                    setIsOpen(false);
                  }}
                  submitLabel={formatMessage({ id: "connectorBuilder.saveInputsForm" })}
                />
              </>
            </ConfigMenuErrorBoundaryComponent>
          </ModalBody>
        </Modal>
      )}
    </>
  );
};
