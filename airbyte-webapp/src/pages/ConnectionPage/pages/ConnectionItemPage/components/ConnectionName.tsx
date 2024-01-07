import { faEdit } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
// import { Button } from "@mui/material";
// import { useTheme } from "@mui/material/styles";
import React, { ChangeEvent, useState } from "react";

import { Input } from "components";
import { CrossIcon } from "components/icons/CrossIcon";
import { TickIcon } from "components/icons/TickIcon";

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
  // const theme = useTheme();
  const { name } = connection;
  const [editingState, setEditingState] = useState(false);
  const [loading, setLoading] = useState(false);
  const [connectionName, setConnectionName] = useState<string | undefined>(connection.name);
  const [connectionNameBackup, setConnectionNameBackup] = useState(connectionName);
  const { mutateAsync: updateConnection } = useUpdateConnection(connection?.connectionId);
  // const isSmallScreen = theme.breakpoints.up("sm");

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

  const onClose = () => {
    setEditingState(false);
    setConnectionName(name);
  };

  const onUpdate = async () => {
    await updateConnectionAsync();
  };

  return (
    <div className={styles.container}>
      {editingState ? (
        <div className={styles.editingContainer}>
          <div className={styles.crossIcon} onClick={onClose} role="presentation">
            <CrossIcon color="#999999" width={16} height={16} />
          </div>
          <div className={styles.inputContainer}>
            <InputWithKeystroke
              className={styles.input}
              value={connectionName}
              onChange={inputChange}
              onEscape={onEscape}
              onEnter={onEnter}
              disabled={loading}
            />
          </div>
          {connectionName && connectionName !== name && (
            <div className={styles.tickIcon} onClick={onUpdate} role="presentation">
              <TickIcon color="#27272A" width={26} height={26} />
            </div>
          )}
        </div>
      ) : (
        <button className={styles.nameContainer} onClick={() => setEditingState(true)}>
          <div>
            <h2>{name}</h2>
          </div>
          <FontAwesomeIcon className={styles.icon} icon={faEdit} />
        </button>

        // <Button
        //   variant="outlined"
        //   size="large"
        //   endIcon={<FontAwesomeIcon className={styles.icon} icon={faEdit} />}
        //   sx={{
        //     color: "rgb(26, 25, 77)!important",
        //     fontSize: isSmallScreen ? "14px" : "22px",
        //     fontWeight: "500",
        //     whiteSpace: "nowrap",
        //     textOverflow: "ellipsis",
        //     backgroundColor: "red",
        //     border: "1px solid #eff0f5!important",
        //     "&:hover": {
        //       cursor: "pointer",
        //       backgroundColor: "#eff0f5",
        //       "& .icon": {
        //         display: "block",
        //         color: "#27272a",
        //       },
        //     },
        //   }}
        //   onClick={() => setEditingState(true)}
        // >
        //   {name}
        // </Button>
      )}
    </div>
  );
};

export default ConnectionName;
