# Securing Airbyte access

Airbyte, in its open-source version, does not support RBAC to manage access to the UI.

However, multiple options exist for the operators to implement access control themselves.

To secure access to Airbyte you have three options:
* Networking restrictions: deploy Airbyte in a private network or use a firewall to filter which IP is allowed to access your host.
* Put Airbyte behind a reverse proxy and handle the access control on the reverse proxy side. 
* If you deployed Airbyte on a cloud provider: 
    * GCP: use the [Identidy-Aware proxy](https://cloud.google.com/iap) service
    * AWS: use the [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html) service

**Non exhaustive** online resources list to set up auth on your reverse proxy:
* [Configure HTTP Basic Auth on NGINX for Airbyte](https://shadabshaukat.medium.com/deploy-and-secure-airbyte-with-nginx-reverse-proxy-basic-authentication-lets-encrypt-ssl-72bee223a4d9)
* [Kubernetes: Basic auth on a Nginx ingress controller](https://kubernetes.github.io/ingress-nginx/examples/auth/basic/)
* [How to set up Okta SSO on an NGINX reverse proxy](https://developer.okta.com/blog/2018/08/28/nginx-auth-request)
* [How to enable HTTP Basic Auth on Caddy](https://caddyserver.com/docs/caddyfile/directives/basicauth)
* [SSO for Traefik](https://github.com/thomseddon/traefik-forward-auth)
