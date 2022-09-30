import { render } from "@testing-library/react";

import { ConnectionReplicationTab } from "./ConnectionReplicationTab";

describe("ConnectionReplicationTab", () => {
  it("should render", () => {
    // TODO: Wrapper component
    expect(render(<ConnectionReplicationTab />)).toMatchSnapshot();
  });
});
