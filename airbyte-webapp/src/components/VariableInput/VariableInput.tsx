import React, { useState } from "react";

import FormHeader from "./components/FormHeader";
import FormItemsList from "./components/FormItemsList";

type VariableInputProps = {
  items: { name: string }[];
  children?: React.ReactNode;
};

const VariableInput: React.FC<VariableInputProps> = ({ items, children }) => {
  const [isEditMode, setIsEditMode] = useState(false);
  const setEditMode = () => setIsEditMode(true);

  if (isEditMode) {
    return <>{children}</>;
  }
  return (
    <>
      <FormHeader itemsCount={items.length} onAddReport={setEditMode} />
      {items.length ? (
        <FormItemsList items={items} onEdit={setEditMode} />
      ) : null}
    </>
  );
};

export { VariableInput };
