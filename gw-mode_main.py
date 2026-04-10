from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator, current_time
from aidefense.runtime.agentsec.exceptions import SecurityPolicyError


### Setup Cisco AI Defense agentsec 

def configure_agentsec() -> bool:
    try:
        from aidefense.runtime import agentsec
        import boto3
        import json
                
        client = boto3.client("secretsmanager", region_name="us-east-1")  # adjust region
        response = client.get_secret_value(SecretId="aid/gwkey")
        secret_string = response["SecretString"]  # or ["SecretBinary"] if binary
        secret_dict = json.loads(secret_string)
        gateway_api_key = secret_dict["AI_DEFENSE_GW_BEDROCK_API_KEY"]

        config = {
            "llm_integration_mode": "gateway",
            "gateway_mode": {
                "llm_mode": "on",
                "llm_defaults": {
                    "fail_open": False,
                    "timeout": 60,
                    "retry": {
                        "total": 3,
                        "backoff_factor": 0.5,
                        "status_codes": [429, 500, 502, 503, 504],
                    },
                },
                "llm_gateways": {
                    "bedrock-1": {
                        "provider": "bedrock",
                        "default": True,
                        "gateway_url": "https://us.gateway.aidefense.security.cisco.com/c5d63378-ed14-4386-81c7-7e8505bd11a0/connections/bfc6d697-3b38-4859-bd02-3f371c6f0a13",
                        "gateway_api_key": gateway_api_key,
                        "auth_mode": "api_key",
            }
                },
            },
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
    try:
        result = agent(user_message)
        return {"result": result.message}
    except SecurityPolicyError as e:
        return {
            "result": "I'm sorry, but your request was blocked by a security policy. Please rephrase your message and try again.",
            "error": "SECURITY_VIOLATION",
            "details": str(e)
        }

if __name__ == "__main__":
    app.run()
