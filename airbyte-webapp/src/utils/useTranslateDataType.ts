import { useMemo } from "react";
import { useIntl } from "react-intl";

export interface AirbyteConnectorData {
  type: string;
  format?: string;
  airbyte_type?: string;
  anyOf?: unknown[];
  oneOf?: unknown[];
}

const getType = (data: AirbyteConnectorData): string => {
  if (data.oneOf || data.anyOf) {
    return "union";
  }
  if (!data.anyOf && !data.oneOf && !data.airbyte_type && !data.format && !data.type) {
    return "unknown";
  }
  return data.airbyte_type ?? data.format ?? data.type;
};

export const useTranslateDataType = (props: AirbyteConnectorData) => {
  const { formatMessage } = useIntl();
  const dataType = useMemo(() => getType(props), [props]);
  return useMemo(
    () =>
      formatMessage({
        id: `airbyte.datatype.${dataType}`,
        defaultMessage: formatMessage({ id: "airbyte.datatype.unknown" }),
      }),
    [dataType, formatMessage]
  );
};

// another ver of useTranslateDataType - without hook and return just string. The old one is left for backward compatibility
export const getDataType = (data: AirbyteConnectorData): string => {
  return `airbyte.datatype.${getType(data)}`;
};
