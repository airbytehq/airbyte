import React, { useEffect, useRef, useState } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { FlexContainer, FlexItem } from "components/ui/Flex";
import { Heading } from "components/ui/Heading";
import { ModalFooter } from "components/ui/Modal/ModalFooter";
import { Text } from "components/ui/Text";

import { StripeCheckoutSessionCreate, StripeCheckoutSessionRead } from "packages/cloud/lib/domain/stripe";

import { ReactComponent as CardSVG } from "./cards.svg";
import { ReactComponent as ConnectorGridSvg } from "./connectorGrid.svg";
import styles from "./EnrollmentModal.module.scss";
import { ReactComponent as FreeSVG } from "./free.svg";
import { ReactComponent as MailSVG } from "./mail.svg";

const STRIPE_SUCCESS_QUERY = "stripeCheckoutSuccess";

interface EnrollmentModalContentProps {
  closeModal: () => void;
  createCheckout: (p: StripeCheckoutSessionCreate) => Promise<StripeCheckoutSessionRead>;
  workspaceId: string;
}

export const EnrollmentModalContent: React.FC<EnrollmentModalContentProps> = ({
  closeModal,
  createCheckout,
  workspaceId,
}) => {
  const isMountedRef = useRef(false);
  const [isLoading, setIsLoading] = useState(false);

  const startStripeCheckout = async () => {
    setIsLoading(true);
    // Use the current URL as a success URL but attach the STRIPE_SUCCESS_QUERY to it
    const successUrl = new URL(window.location.href);
    successUrl.searchParams.set(STRIPE_SUCCESS_QUERY, "true");
    const { stripeUrl } = await createCheckout({
      workspaceId,
      successUrl: successUrl.href,
      cancelUrl: window.location.href,
      stripeMode: "setup",
    });

    // Forward to stripe as soon as we created a checkout session successfully
    if (isMountedRef.current) {
      window.location.assign(stripeUrl);
    }
  };

  // If the user closes the modal while the request is processing, we don't want to redirect them
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  return (
    <>
      <FlexContainer alignItems="center" justifyContent="center" className={styles.header}>
        <div className={styles.headerBackgroundImageContainer}>
          <ConnectorGridSvg />
        </div>
        <div className={styles.pill}>Pill #1</div>
        <div className={styles.pill}>Pill #2</div>
      </FlexContainer>
      <div className={styles.contentWrapper}>
        <Heading size="lg" as="h2" className={styles.contentHeader}>
          <FormattedMessage id="freeConnectorProgram.enrollmentModal.title" />
        </Heading>
        <FlexContainer direction="column" gap="xl">
          <FlexContainer>
            <FlexContainer justifyContent="center" className={styles.iconContainer}>
              <FreeSVG />
            </FlexContainer>
            <FlexContainer direction="column" gap="lg">
              <FormattedMessage
                id="freeConnectorProgram.enrollmentModal.free"
                values={{
                  p1: (content: React.ReactNode) => <Text size="lg">{content}</Text>,
                  p2: (content: React.ReactNode) => <Text size="lg">{content}</Text>,
                }}
              />
            </FlexContainer>
          </FlexContainer>
          <FlexContainer>
            <FlexContainer justifyContent="center" className={styles.iconContainer}>
              <MailSVG />
            </FlexContainer>
            <Text size="lg">
              <FormattedMessage id="freeConnectorProgram.enrollmentModal.emailNotification" />
            </Text>
          </FlexContainer>
          <FlexContainer>
            <FlexContainer justifyContent="center" className={styles.iconContainer}>
              <CardSVG />
            </FlexContainer>
            <Text size="lg">
              <FormattedMessage id="freeConnectorProgram.enrollmentModal.cardOnFile" />
            </Text>
          </FlexContainer>
        </FlexContainer>
      </div>

      <ModalFooter>
        <FlexContainer justifyContent="flex-end" gap="lg">
          <FlexItem>
            <Button variant="secondary" onClick={closeModal}>
              <FormattedMessage id="freeConnectorProgram.enrollmentModal.cancelButtonText" />
            </Button>
          </FlexItem>
          <FlexItem>
            <Button isLoading={isLoading} onClick={startStripeCheckout}>
              <FormattedMessage id="freeConnectorProgram.enrollmentModal.enrollButtonText" />
            </Button>
          </FlexItem>
        </FlexContainer>
      </ModalFooter>
    </>
  );
};
