import React, { useMemo } from "react";
import { Bar, BarChart as BasicBarChart, CartesianGrid, Label, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { barChartColors, theme } from "theme";

type BarChartProps = {
  data: {
    name: string;
    value: number;
  }[];
  legendLabels: string[];
  xLabel?: string;
  yLabel?: string;
};

const BarChart: React.FC<BarChartProps> = ({ data, legendLabels, xLabel, yLabel }) => {
  const chartLinesColor = theme.greyColor20;
  const chartTicksColor = theme.lightTextColor;

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
        {legendLabels.map((barName, key) => (
          <Bar dataKey={barName} key={barName} fill={barChartColors[key]} />
        ))}
      </BasicBarChart>
    </ResponsiveContainer>
  );
};

export default React.memo(BarChart);
