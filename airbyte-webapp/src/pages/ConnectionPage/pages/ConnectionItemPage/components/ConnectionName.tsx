import { faPenToSquare } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { ChangeEvent, createElement, useState } from "react";

import { Input } from "components";

import { buildConnectionUpdate } from "core/domain/connection";
import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useUpdateConnection } from "hooks/services/useConnectionHook";
import withKeystrokeHandler from "utils/withKeystrokeHandler";

import styles from "./ConnectionName.module.scss";

interface ConnectionNameProps {
  connection: WebBackendConnectionRead;
}

const InputWithKeystroke = withKeystrokeHandler(Input);

const ConnectionName: React.FC<ConnectionNameProps> = ({ connection }) => {
  const { name } = connection;
  const [editingState, setEditingState] = useState(false);
  const [loading, setLoading] = useState(false);
  const [connectionName, setConnectionName] = useState<string | undefined>(connection.name);
  const [connectionNameBackup, setConnectionNameBackup] = useState(connectionName);
  const { mutateAsync: updateConnection } = useUpdateConnection();

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

      await updateConnection(buildConnectionUpdate(connection, { name: connectionNameTrimmed }));

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
              defaultFocus
            />
          </div>
        </div>
      ) : (
        //same weird thing happening as pathpopout with typings
        createElement("button", {
          onClick: () => setEditingState(true),
          children: (
            <>
              <div className={styles.nameContainer}>
                <h2>{name}</h2>
              </div>
              <FontAwesomeIcon className={styles.icon} icon={faPenToSquare} />
            </>
          ),
        })
      )}
    </div>
  );
};

export default ConnectionName;
