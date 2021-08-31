# Airbyte Terraform

## Connector Development Infrastructure
We use Terraform to manage any persistent infrastructure used for developing or testing connectors.

Directory structure is roughly as follows:

    ├── aws
    │   ├── demo
    │   │   ├── core
    │   │   └── lb
    │   ├── shared
    │   └── ssh_tunnel
    │       ├── module
    │       │   ├── secrets
    │       │   └── sql
    │       └── user_ssh_public_keys
    └── gcp

Top level is which provider the terraform is for.  Next level is a 
directory containing the project name, or 'shared' for infrastructure (like 
the backend for terraform itself) that crosses projects.

Within each project directory, the top level main.tf contains the infrastructure
for that project, in a high-level format.  The module within it contains the
fine grained details.

Do not place terraform in the top level per-provider directory, as that results in
a monorepo where 'terraform destroy' has a too-wide blast radius.  Instead, create
a separate small terraform instance for each project.  Then plan and destroy only affect
that project and not other unrelated infrastructure.


### Workflow

#### Setup Credentials
**GCP**

Copy the contents of the Lastpass credentials `Connector GCP Terraform Key` into `gcp/connectors/secrets/svc_account_creds.json`. 

Any `secrets` directory in the entire repo is gitignored by default so there is no danger of checking credentials into git.  

**AWS**

You'll find it useful to create an IAM user for yourself and put it in the terraform role, so that 
you can use terraform apply directly against the correct subaccount.  This involves getting logged in to the 
aws console using the lastpass credentials, and then go to IAM and create a user through the GUI.  Download your csv creds
from there.  You can use `aws sts get-caller-identity` to make sure your custom user is recognized.

**Azure**

Coming soon. 



#### Iteration Cycle
To run terraform commands, use the tfenv wrapper available through brew or download: 

    brew install tfenv

Once you have tfenv and are in a directory with a .terraform-version file, just
use the normal terraform commands:

    terraform init
    terraform plan
    terraform apply

**If this is your first time running Terraform** run the `init` command before plan or apply.

To achieve isolation and minimize risks, infrastructure should be isolated by connector 
where feasible (but use your judgment w.r.t costs of duplicate infra). 

To create connector-related resources in any of the clouds:
 <!-- TODO make this iteration cycle clearer w.r.t generating a plan for the PR -->
 
1. Repeatedly modify the relevant terraform and apply as you work.

2. Once satisfied, create a PR with your changes. Please post the 
output of the `terraform plan` command to show the diff in infrastructure 
between the master branch and your PR. This may require deleting all the 
infra you just created and running `terraform apply` one last time.


