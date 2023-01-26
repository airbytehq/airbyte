import React, { useMemo } from "react";
import { FormattedNumber } from "react-intl";
import {
  Bar,
  BarChart as BasicBarChart,
  CartesianGrid,
  Label,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { barChartColors, theme } from "theme";

interface BarChartProps {
  data: Array<{
    name: string;
    value: number;
  }>;
  legendLabels: string[];
  xLabel?: string;
  yLabel?: string;
}

export const BarChart: React.FC<BarChartProps> = React.memo(({ data, legendLabels, xLabel, yLabel }) => {
  const chartLinesColor = theme.grey100;
  const chartTicksColor = theme.grey;
  const chartHoverFill = theme.grey100;

  const width = useMemo(
    () => Math.min(Math.max([...data].sort((a, b) => b.value - a.value)[0].value.toFixed(0).length * 10, 80), 130),
    [data]
  );

  return (
    <ResponsiveContainer>
      <BasicBarChart data={data} margin={{ right: 12, top: 25 }}>
        <CartesianGrid vertical={false} stroke={chartLinesColor} />
        <XAxis
          label={
            <Label
              value={xLabel}
              offset={0}
              position="insideBottom"
              fontSize={11}
              fill={chartTicksColor}
              fontWeight={600}
            />
          }
          dataKey="name"
          axisLine={false}
          tickLine={false}
          stroke={chartTicksColor}
          tick={{ fontSize: "11px" }}
          tickSize={7}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          stroke={chartTicksColor}
          tick={{ fontSize: "11px" }}
          tickSize={10}
          width={width}
        >
          <Label value={yLabel} fontSize={11} fill={chartTicksColor} fontWeight={600} position="top" offset={10} />
        </YAxis>
        <Tooltip
          cursor={{ fill: chartHoverFill }}
          formatter={(value: number) => {
            return [<FormattedNumber value={value} maximumFractionDigits={2} minimumFractionDigits={2} />, yLabel];
          }}
        />
        {legendLabels.map((barName, key) => (
          <Bar key={barName} dataKey={barName} fill={barChartColors[key]} />
        ))}
      </BasicBarChart>
    </ResponsiveContainer>
  );
});
