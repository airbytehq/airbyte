/* eslint-disable jsx-a11y/no-autofocus */
import { faPenToSquare } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { ChangeEvent, useState } from "react";

import { Heading } from "components/ui/Heading";
import { Input } from "components/ui/Input";

import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import withKeystrokeHandler from "utils/withKeystrokeHandler";

import styles from "./ConnectionName.module.scss";

const InputWithKeystroke = withKeystrokeHandler(Input);

export const ConnectionName: React.FC = () => {
  const { connection, updateConnection } = useConnectionEditService();
  const { name } = connection;
  const [editingState, setEditingState] = useState(false);
  const [loading, setLoading] = useState(false);
  const [connectionName, setConnectionName] = useState<string | undefined>(connection.name);
  const [connectionNameBackup, setConnectionNameBackup] = useState(connectionName);

  const inputChange = ({ currentTarget: { value } }: ChangeEvent<HTMLInputElement>) => setConnectionName(value);

  const onEscape: React.KeyboardEventHandler<HTMLInputElement> = (event) => {
    event.stopPropagation();
    setEditingState(false);
    setConnectionName(name);
  };

  const onEnter: React.KeyboardEventHandler<HTMLInputElement> = async (event) => {
    event.stopPropagation();
    await updateConnectionAsync();
  };

  const onBlur = async () => {
    await updateConnectionAsync();
  };

  const updateConnectionAsync = async () => {
    const connectionNameTrimmed = connectionName?.trim();
    if (!connectionNameTrimmed || connection.name === connectionNameTrimmed) {
      setConnectionName(connectionNameBackup);
      setEditingState(false);
      return;
    }

    try {
      setLoading(true);

      await updateConnection({
        name: connectionNameTrimmed,
        connectionId: connection.connectionId,
      });

      setConnectionName(connectionNameTrimmed);
      setConnectionNameBackup(connectionNameTrimmed);
    } catch (e) {
      console.error(e.message);
      setConnectionName(connectionNameBackup);
    } finally {
      setLoading(false);
    }

    setEditingState(false);
  };

  return (
    <div className={styles.container}>
      {editingState ? (
        <div className={styles.editingContainer}>
          <div className={styles.inputContainer} onBlur={onBlur}>
            <InputWithKeystroke
              className={styles.input}
              value={connectionName}
              onChange={inputChange}
              onEscape={onEscape}
              onEnter={onEnter}
              disabled={loading}
              autoFocus
            />
          </div>
        </div>
      ) : (
        <button className={styles.nameContainer} onClick={() => setEditingState(true)}>
          <div>
            <Heading as="h2" size="lg">
              {name}
            </Heading>
          </div>
          <FontAwesomeIcon className={styles.icon} icon={faPenToSquare} />
        </button>
      )}
    </div>
  );
};
