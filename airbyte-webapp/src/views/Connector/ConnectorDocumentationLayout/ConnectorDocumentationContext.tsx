import { createContext, Dispatch, SetStateAction, useContext, useState } from "react";

export const SidePanelStatusContext = createContext<ReturnType<typeof useInitialSidePanelState>>({} as any);

export const useInitialSidePanelState = (
  sidePanelStatus: boolean,
  setSidePanelStatus: Dispatch<SetStateAction<boolean>>
) => {
  return {
    sidePanelStatus,
    setSidePanelStatus,
  };
};

export const useSidePanelContext = () => useContext(SidePanelStatusContext);

export const SidePanelStatusProvider: React.FC = ({ children }) => {
  const [sidePanelStatus, setSidePanelStatus] = useState(false);
  return (
    <SidePanelStatusContext.Provider value={useInitialSidePanelState(sidePanelStatus, setSidePanelStatus)}>
      {children}
    </SidePanelStatusContext.Provider>
  );
};
