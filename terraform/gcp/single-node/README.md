# Terraform

We offer the ability to spin up a single node instance on GCP using Terraform. A new compute instance is spun up in a new VPC which uses a NAT. This instance is Stackdriver monitoring enabled, which grants access to memory usage stats.

In the future we may offer this as a module on the Terraform Registry. For now, you can think of this more of a script that allows you to easily spin up an instance or as a template that allows you to integrate into your existing Terraform project.

### Getting Started
1. Update `providers.tf` to include the correct project, region, and zone. 
1. `gcloud auth application-default login`
2. `terraform init`
3. `terraform apply`

### SSH into instance
```
gcloud beta compute ssh airbyte-prod --zone=us-central1-c
```

### Init script logs
After SSH-ing into the node:
```
cat /var/log/daemon.log | grep startup
```

### Port forward
```
gcloud beta compute ssh airbyte-prod --zone=us-central1-c -- -L 8000:localhost:8000 -L 8001:localhost:8001 -N -f
```

Before using, we'll need to manually modify the env to make this accessible and restart the app.
1. Set API_URL in `.env` to `https://YOUR_IP/api/v1/`.
2. 
```
docker-compose down
docker-compose up -d
```