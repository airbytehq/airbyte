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
  data: any; // TODO: fix type
};

const BarChart: React.FC<BarChartProps> = ({ data }) => {
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
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          stroke={chartTicksColor}
          tick={{ fontSize: "11px" }}
        />
        <Bar dataKey="uv" fill={barChartColors[0]} radius={[4, 4, 0, 0]} />
      </BasicBarChart>
    </ResponsiveContainer>
  );
};

export default BarChart;
