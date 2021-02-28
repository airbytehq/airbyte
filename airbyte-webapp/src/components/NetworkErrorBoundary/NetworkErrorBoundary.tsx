import React from "react";

import ServerIsStarting from "./components/ServerIsStarting";

class NetworkErrorBoundary extends React.Component<
  unknown,
  { unReachServer: boolean }
> {
  constructor(props: Record<string, unknown>) {
    super(props);
    this.state = { unReachServer: false };
  }

  static getDerivedStateFromError(error: {
    message: string;
    status?: number;
  }): { unReachServer: boolean } {
    // Update state so the next render will show the fallback UI.
    return { unReachServer: error.message === "Failed to fetch" };
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  componentDidCatch(): void {}

  render(): React.ReactNode {
    if (this.state.unReachServer) {
      return <ServerIsStarting />;
    }

    return this.props.children;
  }
}

export default NetworkErrorBoundary;
