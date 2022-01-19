import React from "react";
import {
  CartesianGrid,
  BarChart as BasicBarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Bar,
  Label,
} from "recharts";
import { barChartColors, theme } from "theme";

type BarChartProps = {
  data?: {
    name: string;
    value: number | number[];
  }[];
  legendLabels: string[];
  xLabel?: string;
  yLabel?: string;
};

const BarChart: React.FC<BarChartProps> = ({
  data,
  legendLabels,
  xLabel,
  yLabel,
}) => {
  const chartLinesColor = theme.greyColor20;
  const chartTicksColor = theme.lightTextColor;

  return (
    <ResponsiveContainer>
      <BasicBarChart data={data} margin={{ right: 12 }}>
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
        >
          <Label
            value={yLabel}
            angle={-90}
            fontSize={11}
            fill={chartTicksColor}
            fontWeight={600}
          />
        </YAxis>
        {legendLabels.map((barName, key) => (
          <Bar dataKey={barName} fill={barChartColors[key]} />
        ))}
      </BasicBarChart>
    </ResponsiveContainer>
  );
};

export default React.memo(BarChart);
