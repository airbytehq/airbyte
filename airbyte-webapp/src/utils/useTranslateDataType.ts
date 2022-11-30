import { useMemo } from "react";
import { useIntl } from "react-intl";

export interface AirbyteConnectorData {
  type: string;
  format?: string;
  airbyte_type?: string;
  anyOf?: unknown[];
  oneOf?: unknown[];
}

export const useTranslateDataType = (props: AirbyteConnectorData) => {
  const { formatMessage } = useIntl();
  const dataType = useMemo(() => {
    if (props.oneOf || props.anyOf) {
      return "union";
    }
    if (!props.anyOf && !props.oneOf && !props.airbyte_type && !props.format && !props.type) {
      return "unknown";
    }
    return props.airbyte_type ?? props.format ?? props.type;
  }, [props.airbyte_type, props.anyOf, props.format, props.oneOf, props.type]);
  const dataTypeFormatted = useMemo(
    () =>
      formatMessage({
        id: `airbyte.datatype.${dataType}`,
        defaultMessage: formatMessage({ id: "airbyte.datatype.unknown" }),
      }),
    [dataType, formatMessage]
  );

  return dataTypeFormatted;
};
