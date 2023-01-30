import React, { useContext } from "react";

interface Context {
  updatingAll: boolean;
  updatingDefinitionId?: string;
  feedbackList: Record<string, string>;
}

export const useUpdatingState = (): Context => {
  const updatingState = useContext(ConnectorsViewContext);
  if (!updatingState) {
    throw new Error("useUpdatingState must be used within a ConnectorsViewContext.");
  }

  return updatingState;
};

export const ConnectorsViewContext = React.createContext<Context | null>(null);
