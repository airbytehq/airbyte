import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { BarChart } from "components/ui/BarChart";
import { Card } from "components/ui/Card";
import { FlexContainer } from "components/ui/Flex";

import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useGetCloudWorkspaceUsage } from "packages/cloud/services/workspaces/CloudWorkspacesService";

import styles from "./CreditsUsage.module.scss";
import UsagePerConnectionTable from "./UsagePerConnectionTable";

const LegendLabels = ["value"];

const CreditsUsage: React.FC = () => {
  const { formatMessage, formatDate } = useIntl();

  const { workspaceId } = useCurrentWorkspace();
  const data = useGetCloudWorkspaceUsage(workspaceId);

  const chartData = useMemo(
    () =>
      data?.creditConsumptionByDay?.map(({ creditsConsumed, date }) => ({
        name: formatDate(new Date(date[0], date[1] - 1 /* zero-indexed */, date[2]), {
          month: "short",
          day: "numeric",
        }),
        value: creditsConsumed,
      })),
    [data, formatDate]
  );

  return (
    <>
      <Card title={<FormattedMessage id="credits.totalUsage" />} lightPadding>
        <div className={styles.chartWrapper}>
          {data?.creditConsumptionByDay?.length ? (
            <BarChart
              data={chartData}
              legendLabels={LegendLabels}
              xLabel={formatMessage({
                id: "credits.date",
              })}
              yLabel={formatMessage({
                id: "credits.amount",
              })}
            />
          ) : (
            <FlexContainer alignItems="center" justifyContent="center" className={styles.empty}>
              <FormattedMessage id="credits.noData" />
            </FlexContainer>
          )}
        </div>
      </Card>

      <Card title={<FormattedMessage id="credits.usagePerConnection" />} lightPadding className={styles.cardBlock}>
        {data?.creditConsumptionByConnector?.length ? (
          <UsagePerConnectionTable creditConsumption={data.creditConsumptionByConnector} />
        ) : (
          <FlexContainer alignItems="center" justifyContent="center" className={styles.empty}>
            <FormattedMessage id="credits.noData" />
          </FlexContainer>
        )}
      </Card>
    </>
  );
};

export default CreditsUsage;
