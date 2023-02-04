import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { Button } from "components/ui/Button";
import { FlexContainer } from "components/ui/Flex";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";

import { RoutePaths } from "pages/routePaths";

import { ReactComponent as BuilderPromptIcon } from "./builder-prompt-icon.svg";
import styles from "./BuilderPrompt.module.scss";

export const BuilderPrompt: React.FC = () => {
  const navigate = useNavigate();

  return (
    <FlexContainer direction="row" alignItems="center" gap="sm">
      <BuilderPromptIcon className={styles.icon} />
      <FlexContainer direction="column" className={styles.text} gap="sm">
        <Heading as="h2" size="sm" className={styles.title}>
          <FormattedMessage id="connectorBuilder.builderPrompt.title" />
        </Heading>
        <Text size="sm" className={styles.description}>
          <FormattedMessage
            id="connectorBuilder.builderPrompt.description"
            values={{
              adjective: (
                <span className={styles.adjective}>
                  <FormattedMessage id="connectorBuilder.builderPrompt.adjective" />
                </span>
              ),
              noun: (
                <span className={styles.noun}>
                  <FormattedMessage id="connectorBuilder.builderPrompt.noun" />
                </span>
              ),
            }}
          />
        </Text>
      </FlexContainer>
      <Button variant="secondary" onClick={() => navigate(`/${RoutePaths.ConnectorBuilder}`)}>
        <FormattedMessage id="connectorBuilder.builderPrompt.button" />
      </Button>
    </FlexContainer>
  );
};
