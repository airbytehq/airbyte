import React from "react";

import ServerIsStarting from "./components/ServerIsStarting";

class NetworkErrorBoundary extends React.Component<
  {},
  { unReachServer: boolean }
> {
  constructor(props: Object) {
    super(props);
    this.state = { unReachServer: false };
  }

  static getDerivedStateFromError(error: { message: string; status?: number }) {
    // Update state so the next render will show the fallback UI.
    return { unReachServer: error.message === "Failed to fetch" };
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  componentDidCatch() {}

  render() {
    if (this.state.unReachServer) {
      return <ServerIsStarting />;
    }

    return this.props.children;
  }
}

export default NetworkErrorBoundary;
