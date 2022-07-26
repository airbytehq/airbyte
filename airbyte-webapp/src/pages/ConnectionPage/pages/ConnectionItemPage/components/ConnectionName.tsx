import { faPenToSquare } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { ChangeEvent, useState } from "react";
import styled from "styled-components";

import { Input } from "components";

import { buildConnectionUpdate } from "core/domain/connection";
import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useUpdateConnection } from "hooks/services/useConnectionHook";
import addEnterEscFuncForInput from "utils/addEnterEscFuncForInput";

interface Props {
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
  div {
    border: none;
  }
`;

const InputWithKeystroke = addEnterEscFuncForInput(StyledInput);

const ConnectionName: React.FC<Props> = ({ connection }) => {
  const { name } = connection;
  const [editingState, setEditingState] = useState(false);
  const [loading, setLoading] = useState(false);
  const [connectionName, setConnectionName] = useState(connection.name);
  const { mutateAsync: updateConnection } = useUpdateConnection();

  const setEditing = () => {
    setEditingState(true);
  };

  const inputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { value } = event.currentTarget;
    if (value) {
      setConnectionName(event.currentTarget.value);
    }
  };

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
    // Update only when the name is changed
    if (connection.name !== connectionName) {
      setLoading(true);
      await updateConnection(
        buildConnectionUpdate(connection, {
          name: connectionName,
        })
      );
      setLoading(false);
    }

    setEditingState(false);
  };

  return (
    <MainContainer>
      {!editingState && (
        <NameContainer onClick={setEditing}>
          <Name>
            <H2>{name}</H2>
          </Name>
          <Icon icon={faPenToSquare} />
        </NameContainer>
      )}
      {editingState && (
        <EditingContainer>
          <InputContainer>
            <InputWithKeystroke
              value={connectionName}
              onChange={inputChange}
              onBlur={onBlur}
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
