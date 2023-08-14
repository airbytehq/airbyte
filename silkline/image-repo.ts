import * as awsx from "@pulumi/awsx";

export const createRepo = (namePrefix: string) =>
  new awsx.ecr.Repository(`${namePrefix}-ecr-repo`, {
    forceDelete: true,
    name: `${namePrefix}-ecr-repo`,
  });
