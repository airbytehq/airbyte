# Securing Airbyte access

## Reporting Vulnerabilities
⚠️ Please do not file GitHub issues or post on our public forum for security vulnerabilities as they are public! ⚠️

Airbyte takes security issues very seriously. If you have any concern around Airbyte or believe you have uncovered a vulnerability, please get in touch via the e-mail address security@airbyte.io. In the message, try to provide a description of the issue and ideally a way of reproducing it. The security team will get back to you as soon as possible.

Note that this security address should be used only for undisclosed vulnerabilities. Dealing with fixed issues or general questions on how to use the security features should be handled regularly via the user and the dev lists. Please report any security problems to us before disclosing it publicly.

## Access control

Airbyte, in its open-source version, does not support RBAC to manage access to the UI.

However, multiple options exist for the operators to implement access control themselves.

To secure access to Airbyte you have three options:
* Networking restrictions: deploy Airbyte in a private network or use a firewall to filter which IP is allowed to access your host.
* Put Airbyte behind a reverse proxy and handle the access control on the reverse proxy side. 
* If you deployed Airbyte on a cloud provider: 
    * GCP: use the [Identity-Aware proxy](https://cloud.google.com/iap) service
    * AWS: use the [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html) service

**Non exhaustive** online resources list to set up auth on your reverse proxy:
* [Configure HTTP Basic Auth on NGINX for Airbyte](https://shadabshaukat.medium.com/deploy-and-secure-airbyte-with-nginx-reverse-proxy-basic-authentication-lets-encrypt-ssl-72bee223a4d9)
* [Kubernetes: Basic auth on a Nginx ingress controller](https://kubernetes.github.io/ingress-nginx/examples/auth/basic/)
* [How to set up Okta SSO on an NGINX reverse proxy](https://developer.okta.com/blog/2018/08/28/nginx-auth-request)
* [How to enable HTTP Basic Auth on Caddy](https://caddyserver.com/docs/caddyfile/directives/basicauth)
* [SSO for Traefik](https://github.com/thomseddon/traefik-forward-auth)
