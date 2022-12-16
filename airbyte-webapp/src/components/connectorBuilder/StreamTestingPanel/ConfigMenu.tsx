import { faClose, faGear } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useLocalStorage } from "react-use";

import { Button } from "components/ui/Button";
import { CodeEditor } from "components/ui/CodeEditor";
import { InfoBox } from "components/ui/InfoBox";
import { Modal, ModalBody, ModalFooter } from "components/ui/Modal";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { ConnectorForm } from "views/Connector/ConnectorForm";

import styles from "./ConfigMenu.module.scss";

interface ConfigMenuProps {
  className?: string;
}

export const ConfigMenu: React.FC<ConfigMenuProps> = ({ className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { formatMessage } = useIntl();
  const { configString, setConfigString, jsonManifest } = useConnectorBuilderState();

  const [showInputsWarning, setShowInputsWarning] = useLocalStorage<boolean>("connectorBuilderInputsWarning", true);

  const formValues = useMemo(() => {
    return { connectionConfiguration: JSON.parse(configString) };
  }, [configString]);

  const renderInputForm = Boolean(jsonManifest.spec);

  return (
    <>
      <Button
        className={className}
        size="sm"
        variant="secondary"
        onClick={() => setIsOpen(true)}
        icon={<FontAwesomeIcon className={styles.icon} icon={faGear} />}
      />
      {isOpen && (
        <Modal
          size="lg"
          onClose={() => setIsOpen(false)}
          title={<FormattedMessage id="connectorBuilder.configMenuTitle" />}
        >
          <ModalBody
            className={classNames({
              [styles.modalContent]: !renderInputForm,
            })}
          >
            {jsonManifest.spec ? (
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
            ) : (
              <CodeEditor
                value={configString}
                language="json"
                theme="airbyte-light"
                onChange={(val: string | undefined) => {
                  setConfigString(val ?? "");
                }}
              />
            )}
          </ModalBody>
          {!renderInputForm && (
            <ModalFooter>
              <Button onClick={() => setIsOpen(false)}>
                <FormattedMessage id="connectorBuilder.configMenuConfirm" />
              </Button>
            </ModalFooter>
          )}
        </Modal>
      )}
    </>
  );
};
