import React from "react";
import styled from "styled-components";

import { Button } from "components/Button";

import FormHeader from "./components/FormHeader";
import FormItem from "./components/FormItem";
import { FormattedMessage } from "react-intl";

const ItemsList = styled.div`
  background: ${({ theme }) => theme.greyColor0};
  border-radius: 4px;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
`;

const SmallButton = styled(Button)`
  margin-left: 8px;
  padding: 6px 8px 7px;
`;

type VariableInputProps = {
  items: { name: string }[];
  children?: React.ReactNode;
  onStartEdit: (n: number) => void;
  onCancelEdit: () => void;
  onDone: () => void;
  onRemove: (index: number) => void;
  isEditMode: boolean;
};

const VariableInput: React.FC<VariableInputProps> = ({
  onStartEdit,
  onDone,
  onRemove,
  onCancelEdit,
  isEditMode,
  items,
  children,
}) => {
  if (isEditMode) {
    return (
      <>
        {typeof children === "function" ? children() : children}
        <ButtonContainer>
          <SmallButton onClick={onCancelEdit} type="button" secondary>
            <FormattedMessage id="form.cancel" />
          </SmallButton>
          <SmallButton onClick={onDone} type="button">
            <FormattedMessage id="form.done" />
          </SmallButton>
        </ButtonContainer>
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
              onRemove={() => onRemove(key)}
            />
          ))}
        </ItemsList>
      ) : null}
    </>
  );
};

export { VariableInput };
