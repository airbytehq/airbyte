import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ImageBlock from "components/ImageBlock";

interface IProps {
  values: Array<{
    name: string;
    connector: string;
  }>;
  enabled?: boolean;
  entity: "source" | "destination";
}

const Content = styled.div<{ enabled?: boolean }>`
  display: flex;
  align-items: center;
  color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inheret")};
`;

const Image = styled(ImageBlock)`
  margin-right: 6px;
`;

const Connector = styled.div`
  font-weight: normal;
  font-size: 12px;
  line-height: 15px;
  color: ${({ theme }) => theme.greyColor40};
`;

const ConnectEntitiesCell: React.FC<IProps> = ({ values, enabled, entity }) => {
  if (values.length === 1) {
    return (
      <Content enabled={enabled}>
        <Image small />
        <div>
          {values[0].name}
          <Connector>{values[0].connector}</Connector>
        </div>
      </Content>
    );
  }

  if (!values.length) {
    return null;
  }

  return (
    <Content enabled={enabled}>
      <Image num={values.length} />
      <div>
        <FormattedMessage id={`tables.${entity}ConnectWithNum`} values={{ num: values.length }} />
        <Connector>{`${values[0].connector}, ${values[1].connector}${values.length > 2 ? ",..." : ""}`}</Connector>
      </div>
    </Content>
  );
};

export default ConnectEntitiesCell;
