import React from "react";
import {
  CartesianGrid,
  BarChart as BasicBarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Bar,
} from "recharts";
import { barChartColors, theme } from "theme";

type BarChartProps = {
  data?: {
    name: string;
    value: number | number[];
  }[];
  legendLabels: string[];
};

const BarChart: React.FC<BarChartProps> = ({ data, legendLabels }) => {
  const chartLinesColor = theme.greyColor20;
  const chartTicksColor = theme.lightTextColor;

  return (
    <ResponsiveContainer>
      <BasicBarChart data={data} margin={{ right: 12 }}>
        <CartesianGrid vertical={false} stroke={chartLinesColor} />
        <XAxis
          dataKey="name"
          axisLine={false}
          tickLine={false}
          stroke={chartTicksColor}
          tick={{ fontSize: "11px" }}
          tickSize={10}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          stroke={chartTicksColor}
          tick={{ fontSize: "11px" }}
          tickSize={10}
        />
        {legendLabels.map((barName, key) => (
          <Bar dataKey={barName} fill={barChartColors[key]} />
        ))}
      </BasicBarChart>
    </ResponsiveContainer>
  );
};

export default React.memo(BarChart);
