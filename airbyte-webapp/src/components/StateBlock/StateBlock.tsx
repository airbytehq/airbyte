import React, { useState, useEffect } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { H5 } from "components";
import ContentCard from "components/ContentCard";

import { ConnectionStateObject } from "core/request/AirbyteClient";
import { useGetConnectionState } from "hooks/services/useConnectionHook";

type IProps = {
  connectionId: string;
};

const StateBlockComponent = styled(ContentCard)`
  margin-top: 12px;
  padding: 19px 20px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Text = styled.div`
  margin-left: 20px;
  font-size: 11px;
  line-height: 13px;
  color: ${({ theme }) => theme.greyColor40};
  white-space: pre-line;
`;

const CodeBox = styled.pre`
  display: block;
  padding: 10px 30px;
  margin: 0;
  overflow: scroll;
`;

const StateBlock: React.FC<IProps> = ({ connectionId }) => {
  const [state, setState] = useState<ConnectionStateObject>();
  const { mutateAsync: getState } = useGetConnectionState();

  async function loadState() {
    const state = await getState(connectionId);
    if (state) setState(state.state);
  }

  useEffect(() => {
    loadState();
  }, []);

  return (
    <StateBlockComponent>
      <Text>
        <H5 bold>
          <FormattedMessage id={`tables.State.title`} />
        </H5>
        <FormattedMessage id={`tables.State.p1`} />.<br />
        <FormattedMessage id={`tables.State.p2`} />.
      </Text>
      <CodeBox>{state ? formatState(state) : <FormattedMessage id={`tables.State.stateLoading`} />}</CodeBox>
    </StateBlockComponent>
  );
};

const formatState = (state: ConnectionStateObject) => JSON.stringify(state, null, 2);

export default StateBlock;
