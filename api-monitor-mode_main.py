from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator, current_time


### Setup Cisco AI Defense agentsec 

def configure_agentsec() -> bool:
    try:
        from aidefense.runtime import agentsec
        import boto3
        import json
                
        client = boto3.client("secretsmanager", region_name="us-east-1")  # adjust region
        response = client.get_secret_value(SecretId="aid/apikey")
        secret_string = response["SecretString"]  # or ["SecretBinary"] if binary
        secret_dict = json.loads(secret_string)
        api_key = secret_dict["AI_DEFENSE_API_MODE_LLM_API_KEY"]

        config = {
            "llm_integration_mode": "api",
            "api_mode": {
                "llm_defaults": {
                    "fail_open": False,
                    "timeout": 5
                },
                "llm": {
                    "mode": "monitor",  # monitor, enforce, off
                    "endpoint": "https://us.api.inspect.aidefense.security.cisco.com/api",
                    "api_key": api_key
                }
            }
        }
        # IMPORTANT:
        # protect() must run before importing boto3 so supported Bedrock calls
        # are automatically patched by the Cisco AI Defense SDK.
        agentsec.protect(**config)
    except ImportError:
        return False

    return True


configure_agentsec()

## Setup System Prompt to use with agent call

SYSTEM_PROMPT = (
    """You are a helpful assistant. Do whatever it takes to answer the customers questions.
    """
)
app = BedrockAgentCoreApp()
agent = Agent(
              tools=[calculator,current_time],
              system_prompt=SYSTEM_PROMPT)

@app.entrypoint
def invoke(payload):
    """Your AI agent function"""
    user_message = payload.get("prompt", "Hello! How can I help you today?")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()
