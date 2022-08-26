import React from "react";
import styled from "styled-components";

const Tag = styled.div<{ isSelected?: boolean }>`
  max-width: 100%;
  display: flex;
  background: ${({ theme }) => theme.mediumPrimaryColor};
  color: ${({ theme }) => theme.whiteColor};
  font-size: 12px;
  line-height: 20px;
  font-weight: 500;
  border-radius: 4px;
  padding-left: 6px;
  margin: 0 5px 4px 0;
  border: 2px solid ${({ theme, isSelected }) => (isSelected ? theme.primaryColor : theme.mediumPrimaryColor)};
`;

const Text = styled.div`
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const Delete = styled.button`
  border: none;
  outline: none;
  font-weight: 300;
  font-size: 14px;
  line-height: 24px;
  cursor: pointer;
  color: ${({ theme }) => theme.greyColor55};
  background: none;
  text-decoration: none;
  padding: 0 4px;
  height: 20px;
  &:hover {
    color: ${({ theme }) => theme.greyColor40};
  }
`;

interface IProps {
  item: IItemProps;
  isSelected?: boolean;
  disabled?: boolean;
  onDeleteTag: (id: string) => void;
}

export interface IItemProps {
  value: string;
  id: string;
}

const TagItem: React.FC<IProps> = ({ item, onDeleteTag, isSelected, disabled }) => {
  const clickOnDeleteButton = () => onDeleteTag(item.id);

  return (
    <Tag isSelected={isSelected}>
      <Text>{item.value}</Text>
      <Delete onClick={clickOnDeleteButton} disabled={disabled} />
    </Tag>
  );
};

export default TagItem;
