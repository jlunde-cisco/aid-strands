Example AWS Strands and Agentcore Integration via AI Defense Python SDK (which is located here: https://github.com/cisco-ai-defense/ai-defense-python-sdk)

1) Create Application of type API within AI Defense and add connection (copy the generated API key for the connection)
2) Do NOT apply a policy to this connection
3) Add secrets to AWS Secret Manager
4) There are 3 example main.py files in here:
   api-enforce-mode_main.py - This mode enforces based on disposition given by AI Defense and the rules enabled within the config. Do NOT apply policy within AI Defense to the connection
   api-monitor-mode_main.py - This mode only monitors traffic, and will log events within AI Defense.
   gw-mode_main.py - Traffic will be routed through a SaaS proxy, and that proxy will be the policy-enforcement-point based on the applied policy.

An example workflow might look like:

- Install agentcore cli
- Install AWS CLI
- Use Agentcore create to deploy directory structure for container
- Replace DockerFile, pyproject.toml, and main.py with the proper contents from this repo.
- Agentcore Deploy will push to AWS
- Ensure that the IAM role for your project has access to secrets manager and AWS Bedrock marketplace
