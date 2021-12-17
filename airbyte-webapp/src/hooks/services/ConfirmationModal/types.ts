import React from "react";

export type ConfirmationModal = {
  submitButtonText: React.ReactNode;
  title: React.ReactNode;
  text: React.ReactNode;
  onSubmit: () => Promise<void>;
};

export type ConfirmationModalServiceApi = {
  openConfirmationModal: (confirmationModal: ConfirmationModal) => void;
  closeConfirmationModal: () => void;
};

export type ConfirmationModalState = {
  isOpen: boolean;
  confirmationModal: ConfirmationModal | null;
};
