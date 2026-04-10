# AI Defense + AWS Strands & AgentCore Integration

Example integrations of [Cisco AI Defense](https://github.com/cisco-ai-defense/ai-defense-python-sdk) with [AWS Strands Agents](https://strandsagents.com/) and [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/), demonstrating three traffic inspection modes: API enforce, API monitor, and gateway proxy.

---

## How It Works

The AI Defense Python SDK wraps outbound Bedrock API calls via `agentsec.protect()`, which must be called **before** any Bedrock imports. Depending on the mode, AI Defense either inspects traffic inline (API modes) or routes it through a SaaS proxy (gateway mode).

---

## Integration Modes

| File | Mode | Description |
|------|------|-------------|
| `api-enforce-mode_main.py` | **API – Enforce** | Inspects traffic and **blocks** requests that violate enabled rules. Returns a `SecurityPolicyError` on violation. Do **not** apply a policy to the AI Defense connection — enforcement is handled by the SDK config. |
| `api-monitor-mode_main.py` | **API – Monitor** | Inspects traffic and **logs** events to AI Defense without blocking. Useful for baselining or auditing. |
| `gw-mode_main.py` | **Gateway** | Routes LLM traffic through the AI Defense SaaS proxy. The proxy is the policy enforcement point; policy must be applied within AI Defense to the connection. |

### Security Rules (API modes)
The enforce/monitor examples enable the following rules:
- Prompt Injection
- Code Detection
- Harassment / Hate Speech
- PII / PHI / PCI
- Profanity
- Sexual Content & Exploitation
- Social Division & Polarization
- Violence & Public Safety Threats

---

## Prerequisites

- AWS CLI configured
- [Agentcore CLI](https://docs.aws.amazon.com/bedrock/latest/userguide/agent-core.html) installed
- AWS IAM role with access to **Secrets Manager** and **Bedrock Marketplace**
- A Cisco AI Defense account with an application configured

---

## AI Defense Setup

1. In AI Defense, create an **Application** of type **API**.
2. Add a connection and copy the generated API key.
3. **API modes:** Only apply a policy to the connection in monitor mode, not the connection used for enforce mode — enforcement is controlled in the SDK config.
4. **Gateway mode:** Apply your desired policy to the connection in AI Defense.

---

## AWS Secrets Manager

Store your credentials as JSON secrets. The examples expect the following secret IDs and key names:

| Secret ID | Key | Used by |
|-----------|-----|---------|
| `aid/api-key` | `AI_DEFENSE_API_MODE_LLM_API_KEY` | API monitor mode |
| `aid/api-no-policy` | `AI_DEFENSE_API_MODE_LLM_API_KEY` | API enforce mode |
| `aid/gwkey` | `AI_DEFENSE_GW_BEDROCK_API_KEY` | Gateway mode |

> **Note:** Update the `region_name` in each file to match your AWS region.

---

## Deployment to AgentCore

1. Install the AgentCore CLI and AWS CLI.
2. Use `agentcore create` to scaffold a new project directory.
3. Replace the generated `Dockerfile`, `pyproject.toml`, and `main.py` with the files from this repo (choosing the appropriate `*_main.py` for your mode).
4. Run `agentcore deploy` to build and push the container to AWS.
5. Confirm the IAM role for your project has permissions for **Secrets Manager** and **Bedrock Marketplace**.

---

## Related

- [AI Defense Python SDK](https://github.com/cisco-ai-defense/ai-defense-python-sdk)
- [AWS Strands Agents](https://strandsagents.com/)
- [AWS Bedrock AgentCore Docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agent-core.html)
