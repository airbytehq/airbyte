import React, { useContext, useMemo } from "react";

import { WidgetConfigMap } from "../../core/form/types";

// TODO: We need to refactor ServiceForm and have better support for Context (Jamakase)
// Currently, we build uiWidgetInfo and provide it via context here
// Ideally, we should build and provide in same context logic

type Context = {
  widgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (path: string, value: object) => void;
  unfinishedSecrets: Record<string, any>;
  addUnfinishedSecret: (key: string, info?: Record<string, any>) => void;
  removeUnfinishedSecret: (key: string) => void;
  resetUiFormProgress: () => void;
};

const context: Context = {
  widgetsInfo: {},
  unfinishedSecrets: {},
  setUiWidgetsInfo: (_path: string, _value: object) => ({}),
  addUnfinishedSecret: (_key: string, _info?: Record<string, any>) => ({}),
  removeUnfinishedSecret: (_key: string) => ({}),
  resetUiFormProgress: () => ({}),
};

const FormWidgetContext = React.createContext<Context>(context);

const useWidgetInfo = () => useContext(FormWidgetContext);

const WidgetInfoProvider: React.FC<{
  widgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (path: string, value: object) => void;
}> = ({ children, widgetsInfo, setUiWidgetsInfo }) => {
  const ctx = useMemo<Context>(() => {
    const unfinishedSecrets = widgetsInfo["_common.unfinishedSecrets"] ?? {};
    return {
      widgetsInfo,
      setUiWidgetsInfo,
      unfinishedSecrets,
      addUnfinishedSecret: (path, info) =>
        setUiWidgetsInfo("_common.unfinishedSecrets", {
          ...unfinishedSecrets,
          [path]: info ?? {},
        }),
      removeUnfinishedSecret: (path: string) =>
        setUiWidgetsInfo(
          "_common.unfinishedSecrets",
          Object.fromEntries(
            Object.entries(unfinishedSecrets).filter(([key]) => key !== path)
          )
        ),
      resetUiFormProgress: () => {
        setUiWidgetsInfo("_common.unfinishedSecrets", {});
      },
    };
  }, [widgetsInfo, setUiWidgetsInfo]);

  return (
    <FormWidgetContext.Provider value={ctx}>
      {children}
    </FormWidgetContext.Provider>
  );
};

const WidgetInfo = ({
  children,
}: {
  children: (widgetInfo: Context) => React.ReactElement;
}) => {
  const widgetInfo = useWidgetInfo();

  return children(widgetInfo);
};

export { useWidgetInfo, WidgetInfoProvider, WidgetInfo };
