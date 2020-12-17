import React from "react";
import styled from "styled-components";

import { IDataItem } from "./ListItem";
import Text from "./Text";
import ImageBlock from "../../ImageBlock";

export type IProps = {
  item: IDataItem;
};

const ItemView = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: left;
  align-items: center;
`;

const GroupTitle = styled(Text)`
  text-transform: capitalize;
  font-size: 14px;
  line-height: 13px;
`;

const GroupText = styled.div`
  color: ${({ theme }) => theme.greyColor40};
  font-size: 12px;
  line-height: 11px;
`;

const Icon = styled(ImageBlock)`
  margin-right: 6px;
`;

const ValueInput: React.FC<IProps> = ({ item }) => {
  if (item.groupValue || item.groupValueText) {
    return (
      <div>
        <GroupTitle>{item.groupValue || item.groupValueText}</GroupTitle>
        <GroupText>{item.text}</GroupText>
      </div>
    );
  }

  return (
    <ItemView>
      {item.img ? <Icon img={item.img} /> : null}
      <Text>{item.text}</Text>
    </ItemView>
  );
};

export default ValueInput;
