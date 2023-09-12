#!/usr/bin/env bash

set -e

. tools/lib/lib.sh

TUNNEL_PORT=${TUNNEL_PORT:-4242}
SSH_KEY=${SSH_KEY:-~/.ssh/airbyte-app.pem}
INSTANCE_NAME=${INSTANCE_NAME:-demo-airbyte-app}
PRIVATE_LB_NAME=${PRIVATE_LB_NAME:-demo-airbyte-admin-alb}

USAGE="$0 (tunnel|ssh)"

_get_instance_ip() {
  aws --region us-east-1 ec2 describe-instances --filters Name=tag:Name,Values="$INSTANCE_NAME" Name=instance-state-name,Values=running --query "Reservations[0].Instances[0].[PublicIpAddress]" --output text
}

_get_private_alb_dns() {
  aws --region us-east-1 elbv2 describe-load-balancers --names "$PRIVATE_LB_NAME" --query "LoadBalancers[0].[DNSName]" --output text
}

cmd_tunnel() {
  local instance_ip; instance_ip=$(_get_instance_ip)
  local private_alb_dns; private_alb_dns=$(_get_private_alb_dns)

  echo "Tunnel: (Instance: $instance_ip, ALB: $private_alb_dns)"

  echo "Connect to http://localhost:$TUNNEL_PORT"
  ssh -i "$SSH_KEY" -L "$TUNNEL_PORT":"$private_alb_dns":80 -N ec2-user@"$instance_ip"
}

cmd_ssh() {
  local instance_ip; instance_ip=$(_get_instance_ip)

  echo "Ssh: (Instance: $instance_ip)"

  ssh -i "$SSH_KEY" ec2-user@"$instance_ip"
}

main () {
  assert_root

  local cmd=$1; shift || error "Missing command\n\n$USAGE"

  cmd_"$cmd"
}

main "$@"
