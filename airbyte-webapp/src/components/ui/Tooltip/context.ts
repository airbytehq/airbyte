import { createContext, useContext } from "react";

import { TooltipContext } from "./types";

export const tooltipContext = createContext<TooltipContext | null>(null);

export const useTooltipContext = () => {
  const ctx = useContext(tooltipContext);

  if (!ctx) {
    throw new Error("useTooltipContext should be used within tooltipContext.Provider");
  }

  return ctx;
};
