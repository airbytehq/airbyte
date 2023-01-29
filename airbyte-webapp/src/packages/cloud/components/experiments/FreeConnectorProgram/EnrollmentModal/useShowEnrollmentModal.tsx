import { useIntl } from "react-intl";

import { ToastType } from "components/ui/Toast";

import { useModalService } from "hooks/services/Modal";
import { useNotificationService } from "hooks/services/Notification";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { useStripeCheckout } from "packages/cloud/services/stripe/StripeService";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

import { EnrollmentModalContent } from "./EnrollmentModal";

export const useShowEnrollmentModal = () => {
  const { openModal, closeModal } = useModalService();
  const { mutateAsync: createCheckout } = useStripeCheckout();
  const workspaceId = useCurrentWorkspaceId();
  const { emailVerified, sendEmailVerification } = useAuthService();
  const { formatMessage } = useIntl();
  const { registerNotification } = useNotificationService();

  const verifyEmail = () =>
    sendEmailVerification().then(() => {
      registerNotification({
        id: "fcp/verify-email",
        text: formatMessage({ id: "freeConnectorProgram.enrollmentModal.validationEmailConfirmation" }),
        type: ToastType.INFO,
      });
    });

  return {
    showEnrollmentModal: () => {
      openModal({
        title: null,
        content: () => (
          <EnrollmentModalContent
            workspaceId={workspaceId}
            createCheckout={createCheckout}
            closeModal={closeModal}
            emailVerified={emailVerified}
            sendEmailVerification={verifyEmail}
          />
        ),
      });
    },
  };
};
