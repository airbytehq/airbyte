import React from "react";
import styled from "styled-components";

import FormItem from "./FormItem";

const ItemsList = styled.div`
  background: ${({ theme }) => theme.greyColor0};
  border-radius: 4px;
`;

type FormItemsListProps = {
  items: any[];
  onEdit: () => void;
};

const FormItemsList: React.FC<FormItemsListProps> = ({ items, onEdit }) => {
  return (
    <ItemsList>
      {items.map((item, key) => (
        <FormItem name={item.name} key={`form-item-${key}`} onEdit={onEdit} />
      ))}
    </ItemsList>
  );
};

export default FormItemsList;
