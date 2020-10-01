import React from "react";

import ServerIsStarting from "./components/ServerIsStarting";

class NetworkErrorBoundary extends React.Component<
  {},
  { unReachServer: boolean }
> {
  constructor(props: any) {
    super(props);
    this.state = { unReachServer: false };
  }

  static getDerivedStateFromError(error: any) {
    // Update state so the next render will show the fallback UI.
    return { unReachServer: !!error };
  }

  componentDidCatch() {}

  render() {
    if (this.state.unReachServer) {
      return <ServerIsStarting />;
    }

    return this.props.children;
  }
}

export default NetworkErrorBoundary;
