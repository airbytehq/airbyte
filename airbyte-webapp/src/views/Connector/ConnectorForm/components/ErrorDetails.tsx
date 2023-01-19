import { builder } from "@builder.io/sdk";
import { faInfoCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useMemo, useState } from "react";
import { useQuery } from "react-query";

import { Callout } from "components/ui/Callout";
import { FlexContainer, FlexItem } from "components/ui/Flex";
import { Markdown } from "components/ui/Markdown";
import { StatusIcon } from "components/ui/StatusIcon";
import { Text } from "components/ui/Text";

import { ConnectorSpecification } from "core/domain/connector";
import { isSourceDefinitionSpecificationDraft } from "core/domain/connector/source";

import { useConnectorForm } from "../connectorFormContext";
import styles from "./ErrorDetails.module.scss";

interface AnalyticsItem {
  message: string;
  match: string;
  connectors: Array<{ id: string }>;
  priority?: number;
}

interface ErrorDetailsProps {
  errorMessage: string;
}

builder.init("ef8c75a779ea442d8d0b848a849653aa");

export const ErrorDetails: React.FC<ErrorDetailsProps> = ({ errorMessage }) => {
  const { selectedConnectorDefinitionSpecification } = useConnectorForm();
  const specId =
    !isSourceDefinitionSpecificationDraft(selectedConnectorDefinitionSpecification) &&
    ConnectorSpecification.id(selectedConnectorDefinitionSpecification);
  const { data } = useQuery(
    ["connector", "errorAnalytics", specId],
    async () =>
      builder.getAll("connector-error-analytics", {
        fields: "data",
        query: {
          data: {
            connectors: {
              $elemMatch: {
                id: specId,
              },
            },
          },
        },
      }),
    {
      cacheTime: 30 * 60 * 1000,
      staleTime: 30 * 60 * 1000,
      select: (response) => response as unknown as Array<{ data: AnalyticsItem }>,
    }
  );
  const [analytic, setAnalytic] = useState<AnalyticsItem>();

  useMemo(() => {
    if (!data) {
      setAnalytic(undefined);
    } else {
      let analytic: AnalyticsItem | undefined = undefined;
      for (const { data: entry } of data) {
        if (new RegExp(entry.match.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replaceAll("*", ".*")).test(errorMessage)) {
          if (!analytic || (entry.priority ?? 0) > (analytic.priority ?? 0)) {
            analytic = entry;
          }
        }
      }
      setAnalytic(analytic);
    }
  }, [data, errorMessage]);

  return (
    <FlexContainer direction="column" gap="md" className={styles.container}>
      <Callout variant="error">
        <FlexContainer direction="column">
          <FlexContainer alignItems="center" gap="none">
            <FlexItem grow={false}>
              <StatusIcon status="error" />
            </FlexItem>
            <FlexItem grow>
              <Text bold>The connection tests failed with the following error:</Text>
            </FlexItem>
          </FlexContainer>
          <Text>{errorMessage}</Text>
        </FlexContainer>
      </Callout>
      {analytic && (
        <Callout variant="info">
          <FontAwesomeIcon icon={faInfoCircle} />
          <Text size="md">
            <Markdown className={styles.analyticsMessage} content={analytic.message} />
          </Text>
        </Callout>
      )}
    </FlexContainer>
  );
};
