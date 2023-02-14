import { FormattedMessage } from "react-intl";
import { useResizeDetector } from "react-resize-detector";
import { useNavigate } from "react-router-dom";

import { Button } from "components/ui/Button";
import { FlexContainer } from "components/ui/Flex";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";

import { ReactComponent as BuilderPromptIcon } from "./builder-prompt-icon.svg";
import styles from "./BuilderPrompt.module.scss";

interface BuilderPromptProps {
  builderRoutePath: string;
}

export const BuilderPrompt: React.FC<BuilderPromptProps> = ({ builderRoutePath }) => {
  const navigate = useNavigate();
  const { width, ref } = useResizeDetector();
  const applyNarrowLayout = Boolean(width && width < 460);

  return (
    <FlexContainer
      direction={applyNarrowLayout ? "column" : "row"}
      alignItems="center"
      justifyContent="space-between"
      gap="md"
      ref={ref}
    >
      <FlexContainer direction="row" justifyContent="flex-start" alignItems="center" gap="md">
        <BuilderPromptIcon className={styles.icon} />
        <FlexContainer direction="column" gap="sm">
          <Heading as="h2" size="sm">
            <FormattedMessage id="connectorBuilder.builderPrompt.title" />
          </Heading>
          <Text size="sm" className={styles.description}>
            <FormattedMessage
              id="connectorBuilder.builderPrompt.description"
              values={{
                adjective: (
                  <Text as="span" bold gradient size="sm">
                    <FormattedMessage id="connectorBuilder.builderPrompt.adjective" />
                  </Text>
                ),
                noun: (
                  <Text as="span" bold size="sm" className={styles.description}>
                    <FormattedMessage id="connectorBuilder.builderPrompt.noun" />
                  </Text>
                ),
              }}
            />
          </Text>
        </FlexContainer>
      </FlexContainer>
      <Button variant="secondary" onClick={() => navigate(builderRoutePath)} full={applyNarrowLayout}>
        <FormattedMessage id="connectorBuilder.builderPrompt.button" />
      </Button>
    </FlexContainer>
  );
};
