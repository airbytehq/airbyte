import { renderHook, act } from "@testing-library/react-hooks";
import { MockResolver } from "@rest-hooks/test";

import useConnector from "./useConnector";

const results = [];

test("should not call updateVersion for deprecated call", () => {
  const wrapper = ({ children }) => (
    <MockResolver results={results}></MockResolver>
  );
  const { result } = renderHook(() => useConnector());

  act(() => {
    result.current.updateAllSourceVersions;
  });
});
