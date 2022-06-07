import { faPenToSquare } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { ChangeEvent, useState } from "react";
import styled from "styled-components";

import { Input } from "components";

import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useUpdateConnection } from "hooks/services/useConnectionHook";
import addEnterEscFuncForInput from "utils/addEnterEscFuncForInput";

interface ConnectionNameProps {
  connection: WebBackendConnectionRead;
}

const MainContainer = styled.div`
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Icon = styled(FontAwesomeIcon)`
  display: none;
  position: absolute;
  right: 20px;
  font-size: 18px;
  color: ${({ theme }) => theme.primaryColor};
`;

const NameContainer = styled.div`
  width: 650px;
  background-color: rgba(255, 235, 215, 0.4);
  display: flex;
  align-items: center;
  position: relative;
  padding: 0 20px;
  border-radius: 8px;
  border: 1px solid rgba(255, 235, 215, 0.4);

  &:hover {
    cursor: pointer;
    border: ${({ theme }) => `1px solid ${theme.primaryColor}`};
    background-color: ${({ theme }) => theme.primaryColor12};
  }

  &:hover ${Icon} {
    display: block;
  }
`;

const EditingContainer = styled.div`
  width: 650px;
  display: flex;
  background-color: white;
  justify-content: center;
  align-items: center;
  border-radius: 8px;
  border: ${({ theme }) => `1px solid ${theme.primaryColor}`};
`;

const InputContainer = styled.div`
  height: 50px;
  width: 100%;

  div {
    border-radius: 8px;
    border: none;
    box-shadow: none;
    background-color: white !important;
  }
`;

const Name = styled.div`
  flex-grow: 1;
`;

const H2 = styled.h2`
  font-weight: 700;
  font-size: 24px;
  line-height: 29px;
  text-align: center;
  color: #1a194d;
  margin: 10px;
`;

const StyledInput = styled(Input)`
  border-radius: 8px;
  background-color: white;
  font-size: 24px;
  height: 50px;
  text-align: center;
  div {
    border: none;
  }
`;

const InputWithKeystroke = addEnterEscFuncForInput(StyledInput);

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
    if (connectionName === undefined || connection.name === connectionName.trim() || !connectionName.trim()) {
      setConnectionName(connectionNameBackup);
      setEditingState(false);
      return;
    }

    const connectionNameTrimmed = connectionName.trim();
    try {
      setLoading(true);

      await updateConnection({
        connectionId: connection.connectionId,
        syncCatalog: connection.syncCatalog,
        prefix: connection.prefix,
        schedule: connection.schedule || null,
        namespaceDefinition: connection.namespaceDefinition,
        namespaceFormat: connection.namespaceFormat,
        operations: connection.operations,
        status: connection.status,
        name: connectionNameTrimmed,
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
    <MainContainer>
      {!editingState && (
        <NameContainer onClick={() => setEditingState(true)}>
          <Name>
            <H2>{name}</H2>
          </Name>
          <Icon icon={faPenToSquare} />
        </NameContainer>
      )}
      {editingState && (
        <EditingContainer>
          <InputContainer onBlur={onBlur}>
            <InputWithKeystroke
              value={connectionName}
              onChange={inputChange}
              onEscape={onEscape}
              onEnter={onEnter}
              disabled={loading}
              defaultFocus
            />
          </InputContainer>
        </EditingContainer>
      )}
    </MainContainer>
  );
};

export default ConnectionName;
