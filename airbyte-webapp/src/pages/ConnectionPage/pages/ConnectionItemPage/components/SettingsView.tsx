import React from "react";
import styled from "styled-components";

import useConnection from "hooks/services/useConnectionHook";
import DeleteBlock from "components/DeleteBlock";

type IProps = {
  connectionId: string;
};

const Content = styled.div`
  max-width: 647px;
  margin: 0 auto;
  padding-bottom: 10px;
`;

const SettingsView: React.FC<IProps> = ({ connectionId }) => {
  const { deleteConnection } = useConnection();

  const onDelete = () => deleteConnection({ connectionId });

  return (
    <Content>
      <DeleteBlock type="connection" onDelete={onDelete} />
    </Content>
  );
};

export default SettingsView;
