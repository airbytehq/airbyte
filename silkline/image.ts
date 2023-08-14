import * as awsx from "@pulumi/awsx";
import { Output } from "@pulumi/pulumi";

// Build and publish our application's container image from ./app to the ECR repository
export const createImage = (
  namePrefix: string,
  repositoryUrl: Output<string>,
  path: string,
  target?: string
) =>
  new awsx.ecr.Image(`${namePrefix}-image`, {
    repositoryUrl,
    path,
    target,
  });
