import { faClose, faUser } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useLocalStorage } from "react-use";

import { Button } from "components/ui/Button";
import { InfoBox } from "components/ui/InfoBox";
import { Modal, ModalBody } from "components/ui/Modal";
import { NumberBadge } from "components/ui/NumberBadge";
import { Tooltip } from "components/ui/Tooltip";

import { SourceDefinitionSpecificationDraft } from "core/domain/connector";
import { StreamReadRequestBodyConfig } from "core/request/ConnectorBuilderClient";
import { useConnectorBuilderTestState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { useConnectorBuilderFormState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { ConnectorForm } from "views/Connector/ConnectorForm";

import styles from "./ConfigMenu.module.scss";
import { ConfigMenuErrorBoundaryComponent } from "./ConfigMenuErrorBoundary";

interface ConfigMenuProps {
  className?: string;
  testInputJsonErrors: number;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export const ConfigMenu: React.FC<ConfigMenuProps> = ({ className, testInputJsonErrors, isOpen, setIsOpen }) => {
  const { formatMessage } = useIntl();
  const { jsonManifest, editorView, setEditorView } = useConnectorBuilderFormState();

  const { testInputJson, setTestInputJson } = useConnectorBuilderTestState();

  const [showInputsWarning, setShowInputsWarning] = useLocalStorage<boolean>("connectorBuilderInputsWarning", true);

  const switchToYaml = () => {
    setEditorView("yaml");
    setIsOpen(false);
  };

  const connectorDefinitionSpecification: SourceDefinitionSpecificationDraft | undefined = useMemo(
    () =>
      jsonManifest.spec
        ? {
            documentationUrl: jsonManifest.spec.documentation_url,
            connectionSpecification: jsonManifest.spec.connection_specification,
          }
        : undefined,
    [jsonManifest]
  );

  return (
    <>
      <Tooltip
        control={
          <>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => setIsOpen(true)}
              disabled={
                !jsonManifest.spec ||
                Object.keys(jsonManifest.spec.connection_specification.properties || {}).length === 0
              }
              icon={<FontAwesomeIcon className={styles.icon} icon={faUser} />}
            >
              <FormattedMessage id="connectorBuilder.inputsButton" />
            </Button>
            {testInputJsonErrors > 0 && (
              <NumberBadge className={styles.inputsErrorBadge} value={testInputJsonErrors} color="red" />
            )}
          </>
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
      {isOpen && connectorDefinitionSpecification && (
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
                  selectedConnectorDefinitionSpecification={connectorDefinitionSpecification}
                  formValues={{ connectionConfiguration: testInputJson }}
                  onSubmit={async (values) => {
                    setTestInputJson(values.connectionConfiguration as StreamReadRequestBodyConfig);
                    setIsOpen(false);
                  }}
                  onCancel={() => {
                    setIsOpen(false);
                  }}
                  onReset={() => {
                    setTestInputJson({});
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
