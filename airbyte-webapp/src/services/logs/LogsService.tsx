import { useMutation } from "react-query";

import { LogsService } from "core/domain/logs/LogsService";
import { useInitService } from "services/useInitService";

// import { useConfig } from "../../config";
import { LogsRequestBody } from "../../core/request/AirbyteClient";
import { useDefaultRequestMiddlewares } from "../useDefaultRequestMiddlewares";

export const logsKeys = {
  all: ["logs"] as const,
  details: () => [...logsKeys.all, "detail"] as const,
  detail: (id: number | string) => [...logsKeys.details(), id] as const,
};

function useGetLogsService(): LogsService {
  // const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();
  return useInitService(
    () => new LogsService(process.env.REACT_APP_API_URL as string, middlewares),
    [process.env.REACT_APP_API_URL as string, middlewares]
  );
}

export function useGetLogs() {
  const service = useGetLogsService();

  return useMutation((payload: LogsRequestBody) => service.get(payload)).mutateAsync;
}
