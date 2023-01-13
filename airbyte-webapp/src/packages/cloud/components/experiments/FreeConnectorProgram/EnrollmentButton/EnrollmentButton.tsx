import React from "react";
import { FormattedMessage } from "react-intl";

import { Button, ButtonVariant } from "components/ui/Button";
import { FlexContainer, FlexItem } from "components/ui/Flex";

import { useModalService } from "hooks/services/Modal";
import { useStripeCheckout } from "packages/cloud/services/stripe/StripeService";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

import { EnrollmentModalContent } from "./EnrollmentModal";

interface FCPEnrollmentButtonProps {
  buttonTextKey?: string;
  variant?: ButtonVariant;
}

export const FCPEnrollmentButton: React.FC<FCPEnrollmentButtonProps> = ({
  buttonTextKey = "freeConnectorProgram.enrollmentModal.enrollButtonText",
  variant = "primary",
}) => {
  const { openModal, closeModal } = useModalService();
  const { mutateAsync: createCheckout } = useStripeCheckout();
  const workspaceId = useCurrentWorkspaceId();

  const showEnrollmentModal = () => {
    openModal({
      title: null,
      content: () => (
        <EnrollmentModalContent workspaceId={workspaceId} createCheckout={createCheckout} closeModal={closeModal} />
      ),
    });
  };

  return (
    <FlexContainer justifyContent="flex-end">
      <FlexItem>
        <Button onClick={() => showEnrollmentModal()} variant={variant}>
          <FormattedMessage id={buttonTextKey} />
        </Button>
      </FlexItem>
    </FlexContainer>
  );
};
