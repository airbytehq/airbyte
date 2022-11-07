import React, { useContext } from "react";

const Context = React.createContext<EditControlsServiceContext | null>(null);

export interface EditControlsServiceContext {
  setVisible: (value: boolean) => void;
}

export const EditControlsServiceProvider: React.FC<React.PropsWithChildren<EditControlsServiceContext>> = ({
  children,
  setVisible,
}) => {
  const ctx: EditControlsServiceContext = {
    setVisible,
  };

  return <Context.Provider value={ctx}>{children}</Context.Provider>;
};

export const useEditControlsService = (): EditControlsServiceContext => {
  const ctx = useContext(Context);

  if (!ctx) {
    throw new Error("useEditControlsService should be used within EditControlsServiceProvider");
  }

  return ctx;
};
