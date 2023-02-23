import { PropsWithChildren, Suspense } from "react";

export const TestSuspenseBoundary: React.FC<PropsWithChildren<unknown>> = ({ children }) => {
  return <Suspense fallback={<div>Test suspense boundary</div>}>{children}</Suspense>;
};
