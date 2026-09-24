# Fabric Workspace Setup

This guide details how to provision the Fabric environment without incurring unexpected costs.

## Prerequisites

- A Microsoft Entra ID (Azure AD) account.
- **Trial Eligibility**: You can use the free 60-day Microsoft Fabric trial.
- **Azure for Students**: If you are deploying the optional Azure AI Search component, an Azure for Students subscription can cover the costs.

## Warning: Infrastructure Not Automatically Deployed

DataSentinel currently **does not** automatically deploy Azure or Fabric resources via Terraform or ARM templates. You must manually provision the Fabric workspace.

## Step-by-Step Provisioning

1. Go to [app.fabric.microsoft.com](https://app.fabric.microsoft.com).
2. Start your Free Trial if prompted.
3. Click **Workspaces** -> **New workspace**.
4. Name it DataSentinel_Workspace.
5. Under Advanced, select **Trial** or **Fabric capacity**.

## Cost Safety & Free Alternatives

- **Storage**: OneLake storage is extremely cheap, but keep an eye on streaming table sizes.
- **Compute**: Fabric Trial provides 64 Capacity Units (CUs). Turn off streaming when not actively developing.
- **AI**: By default, DataSentinel uses local LangGraph and Ollama. You **do not** need to provision Azure OpenAI unless you specifically configure it.

## Required Services (Fabric Mode)
- OneLake
- Lakehouse
- Data Factory
- Eventstream
- Eventhouse (KQL Database)

## Optional Services
- Azure AI Search (for Cloud RAG)
- Azure OpenAI (for Cloud Agent)
