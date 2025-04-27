cd infra/
terraform init
terraform plan -out=tfplan
terraform apply tfplan
terraform output -json > ../shared/infra_outputs.auto.tfvars.json

cd data_feed
terraform init
terraform plan -var-file=../shared/infra_outputs.auto.tfvars.json -out=tfplan
terraform apply tfplan

cd apps/inventory
terraform init
terraform plan -var-file=../../shared/infra_outputs.auto.tfvars.json -out=tfplan
terraform apply tfplan
