import React, { createContext, useContext, useMemo } from "react";
import { useToggle } from "react-use";

import { InviteUsersModal } from "packages/cloud/views/users/InviteUsersModal";

interface InviteUsersModalServiceContext {
  isInviteUsersModalOpen: boolean;
  toggleInviteUsersModalOpen: (open?: boolean) => void;
}

const inviteUsersModalServiceContext = createContext<InviteUsersModalServiceContext | null>(null);
const { Provider } = inviteUsersModalServiceContext;

export const useInviteUsersModalService = () => {
  const ctx = useContext(inviteUsersModalServiceContext);
  if (!ctx) {
    throw new Error("useInviteUsersModalService should be use within InviteUsersModalServiceProvider");
  }
  return ctx;
};

interface InviteUsersModalServiceProviderProps {
  invitedFrom: "source" | "destination" | "user.settings";
}
export const InviteUsersModalServiceProvider: React.FC<
  React.PropsWithChildren<InviteUsersModalServiceProviderProps>
> = ({ children, invitedFrom }) => {
  const [isOpen, toggleIsOpen] = useToggle(false);

  const contextValue = useMemo<InviteUsersModalServiceContext>(
    () => ({
      isInviteUsersModalOpen: isOpen,
      toggleInviteUsersModalOpen: toggleIsOpen,
    }),
    [isOpen, toggleIsOpen]
  );

  return (
    <Provider value={contextValue}>
      {children}
      {isOpen && <InviteUsersModal onClose={toggleIsOpen} invitedFrom={invitedFrom} />}
    </Provider>
  );
};
