import classNames from "classnames";
import { useState } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { CodeEditor } from "components/ui/CodeEditor";
import { Modal, ModalBody, ModalFooter } from "components/ui/Modal";

import styles from "./ConfigMenu.module.scss";

interface ConfigMenuProps {
  className?: string;
}

export const ConfigMenu: React.FC<ConfigMenuProps> = ({ className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [configValue, setConfigValue] = useState("{\n  \n}");

  return (
    <>
      <Button
        className={classNames(className, styles.openModalButton)}
        variant="secondary"
        onClick={() => setIsOpen(true)}
      >
        <FormattedMessage id="connectorBuilder.configMenuTitle" />
      </Button>
      {isOpen && (
        <Modal onClose={() => setIsOpen(false)} title={<FormattedMessage id="connectorBuilder.configMenuTitle" />}>
          <ModalBody className={styles.modalContent}>
            <CodeEditor
              value={configValue}
              language="json"
              theme="airbyte"
              onChange={(val: string | undefined) => {
                setConfigValue(val ?? "");
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
