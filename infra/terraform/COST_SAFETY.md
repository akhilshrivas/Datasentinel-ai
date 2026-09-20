# Azure Cost Safety & Free Tier Usage

This project uses Azure services designed to fit within the Azure for Students / Free Tier allowance.

## Resources Provisioned
1. **Resource Group**: Free.
2. **Storage Account (Standard LRS)**: First 5GB is free for 12 months.
3. **Log Analytics Workspace**: Free up to 5GB/month.
4. **Container Apps Environment**: Serverless consumption tier. 180,000 vCPU-seconds, 360,000 GiB-seconds, and 2 million requests free per month.
5. **Static Web Apps**: Free tier available for frontend.
6. **Azure AI Search (Optional)**: Defaults to Free tier (1 index, 50MB limit).

## Important Commands to verify Safety
Before applying Terraform, run:
`az account show`

Always review the plan:
`terraform plan`

Never run `terraform destroy` without explicit approval, though it will just remove the demo resources.
