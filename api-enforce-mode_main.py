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
        response = client.get_secret_value(SecretId="aid/api-no-policy")
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
                    "mode": "enforce",  # monitor, enforce, off
                    "endpoint": "https://us.api.inspect.aidefense.security.cisco.com/api",
                    "api_key": api_key,
                    "rules": [
                        {"rule_name": "Prompt Injection"},
                        {"rule_name": "Code Detection"},
                        {"rule_name": "Harassment"},
                        {"rule_name": "Hate Speech"},
                        {"rule_name": "PII"},
                        {"rule_name": "PHI"},
                        {"rule_name": "PCI"},
                        {"rule_name": "Profanity"},
                        {"rule_name": "Sexual Content & Exploitation"},
                        {"rule_name": "Social Division & Polarization"},
                        {"rule_name": "Violence & Public Safety Threats"},

                        ],
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
