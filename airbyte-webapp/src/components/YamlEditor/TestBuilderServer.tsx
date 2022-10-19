import { Button } from "components/ui/Button";

import { useConfig } from "config";

export const TestBuilderServer: React.FC<unknown> = () => {
  const config = useConfig();
  const url = config.connectorBuilderUrl;

  const handleClick = async () => {
    const response = await fetch(url, {
      method: "get",
    });

    alert(response);
  };

  return <Button onClick={handleClick}>Test Call to Server</Button>;
};
