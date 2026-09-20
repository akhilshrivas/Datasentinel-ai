import os
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from agents.tools import (
    run_readonly_sql,
    get_pipeline_status,
    get_latest_quality_results,
    get_latest_anomalies,
    get_table_schema,
    search_runbook
)

def get_llm():
    provider = os.getenv("AI_PROVIDER", "ollama")
    if provider == "ollama":
        return ChatOpenAI(
            base_url=os.getenv("OLLAMA_API_URL", "http://localhost:11434/v1"),
            api_key="ollama", # required but not used
            model="llama3" # or whichever model is pulled
        )
    else:
        return ChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2023-05-15",
            deployment_name="gpt-4"
        )

def create_agent():
    llm = get_llm()
    
    tools = [
        Tool(
            name="RunSQL",
            func=run_readonly_sql,
            description="Executes a read-only SQL query against the analytics database. Useful for answering data questions."
        ),
        Tool(
            name="GetPipelineStatus",
            func=lambda _: get_pipeline_status(),
            description="Returns the status of the latest pipeline runs."
        ),
        Tool(
            name="GetQualityResults",
            func=lambda _: get_latest_quality_results(),
            description="Returns the most recent data quality validation results."
        ),
        Tool(
            name="GetAnomalies",
            func=lambda _: get_latest_anomalies(),
            description="Returns the most recent anomalies detected in the metrics."
        ),
        Tool(
            name="GetTableSchema",
            func=get_table_schema,
            description="Gets the schema (columns and types) for a given table. Argument should be the table name."
        ),
        Tool(
            name="SearchRunbook",
            func=search_runbook,
            description="Searches the knowledge base for runbooks and documentation. Pass the error or incident as the query."
        )
    ]
    
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent

def investigate_incident(query: str):
    agent = create_agent()
    system_prompt = f"""
    You are an AI Data Reliability Assistant.
    Investigate the following issue: {query}
    
    Follow this workflow:
    1. Check pipeline status.
    2. Check quality results.
    3. Check anomaly results.
    4. If needed, check table schemas and query the database.
    5. Search the runbook for remediation.
    
    Provide a root cause analysis and a remediation recommendation based ONLY on the data you found. Do not hallucinate facts.
    """
    
    return agent.run(system_prompt)

if __name__ == "__main__":
    # Test
    print(investigate_incident("Why did revenue drop yesterday?"))
