import React from "react";
import styled from "styled-components";

import { Button } from "components/Button";

import FormHeader from "./components/FormHeader";
import FormItem from "./components/FormItem";

const ItemsList = styled.div`
  background: ${({ theme }) => theme.greyColor0};
  border-radius: 4px;
`;

type VariableInputProps = {
  items: { name: string }[];
  children?: React.ReactNode;
  onStartEdit: (n: number) => void;
  onCancelEdit: () => void;
  onDone: () => void;
  isEditMode: boolean;
};

const VariableInput: React.FC<VariableInputProps> = ({
  onStartEdit,
  onDone,
  onCancelEdit,
  isEditMode,
  items,
  children,
}) => {
  if (isEditMode) {
    return (
      <>
        {children}
        <Button secondary onClick={onDone}>
          cancel
        </Button>
        <Button onClick={onCancelEdit}>save</Button>
      </>
    );
  }

  return (
    <>
      <FormHeader
        itemsCount={items.length}
        onAddItem={() => onStartEdit(items.length)}
      />
      {items.length ? (
        <ItemsList>
          {items.map((item, key) => (
            <FormItem
              key={`form-item-${key}`}
              name={item.name}
              onEdit={() => onStartEdit(key)}
              onRemove={() => onStartEdit(key)}
            />
          ))}
        </ItemsList>
      ) : null}
    </>
  );
};

export { VariableInput };
