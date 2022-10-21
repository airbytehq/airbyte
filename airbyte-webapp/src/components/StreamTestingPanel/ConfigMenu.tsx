import { faGear } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { useState } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { CodeEditor } from "components/ui/CodeEditor";
import { Modal, ModalBody, ModalFooter } from "components/ui/Modal";

import { useConnectorBuilderState } from "services/connector-builder/ConnectorBuilderStateService";

import styles from "./ConfigMenu.module.scss";

interface ConfigMenuProps {
  className?: string;
}

export const ConfigMenu: React.FC<ConfigMenuProps> = ({ className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { configString, setConfigString } = useConnectorBuilderState();

  return (
    <>
      <Button
        className={classNames(className, styles.openModalButton)}
        variant="secondary"
        onClick={() => setIsOpen(true)}
        icon={<FontAwesomeIcon className={styles.icon} icon={faGear} />}
      />
      {isOpen && (
        <Modal onClose={() => setIsOpen(false)} title={<FormattedMessage id="connectorBuilder.configMenuTitle" />}>
          <ModalBody className={styles.modalContent}>
            <CodeEditor
              value={configString}
              language="json"
              theme="airbyte"
              onChange={(val: string | undefined) => {
                setConfigString(val ?? "");
              }}
            />
          </ModalBody>
          <ModalFooter>
            <Button onClick={() => setIsOpen(false)}>
              <FormattedMessage id="connectorBuilder.configMenuConfirm" />
            </Button>
          </ModalFooter>
        </Modal>
      )}
    </>
  );
};
