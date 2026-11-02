"""Northstar harness composition root. Uses deepagents and the middleware MCP server."""

from __future__ import annotations

from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatResult
from langchain_core.tools import StructuredTool

from config import HarnessConfig
from mcp_client import CompanyMcpClient
from stages import company_context

_CUSTOMER_BRIEF = (
    "look up a customer's recorded goal and contact before answering or drafting. "
    "Cite the record id when the facts are used. The tool does not change data."
)
_ISSUE_LOOKUP = (
    "look up a customer's reported engineering issue. "
    "The lookup does not resolve or modify the issue."
)
_REVENUE_SUMMARY = (
    "read the recorded revenue total for a quarter. Do not estimate a missing quarter. "
    "The tool does not modify financial records."
)
_SEND_PROPOSAL = (
    "record a customer proposal in the local outbox. The body carries Customer goal, "
    "Proposed scope, Assumptions, and Next steps. Repeated identical proposals reuse "
    "the receipt. The tool does not send email."
)


class SilentModel(BaseChatModel):
    """Local stand-in. Construction binds it. A call would mean a provider request."""

    calls: int = 0

    @property
    def _llm_type(self) -> str:
        return "silent"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        type(self).calls += 1
        raise RuntimeError("scripted construction must not call a model provider")

    def bind_tools(self, tools: Any, **kwargs: Any) -> "SilentModel":
        return self


ROLE_TOOLS = {
    "sales": ("customer_brief", "send_proposal"),
    "engineering": ("customer_brief", "issue_lookup"),
    "finance": ("customer_brief", "revenue_summary"),
}


def tools_for_role(config: HarnessConfig) -> list[StructuredTool]:
    """Model tool list. The role is already bound on the config. It is not a tool argument."""
    allowed = ROLE_TOOLS.get(config.role)
    if allowed is None:
        raise ValueError(f"Unknown employee role: {config.role}.")
    by_name = {tool.name: tool for tool in company_tools(config)}
    return [by_name[name] for name in allowed]


def company_tools(config: HarnessConfig) -> list[StructuredTool]:

    client = CompanyMcpClient(config.mcp_url, config.role)

    def customer_brief(customer: str) -> Any:
        return client.call("customer_brief", {"customer": customer})

    def issue_lookup(customer: str) -> Any:
        return client.call("issue_lookup", {"customer": customer})

    def revenue_summary(quarter: str) -> Any:
        return client.call("revenue_summary", {"quarter": quarter})

    def send_proposal(customer: str, body: str) -> Any:
        return client.call("send_proposal", {"customer": customer, "body": body})

    specs = (
        (customer_brief, _CUSTOMER_BRIEF),
        (issue_lookup, _ISSUE_LOOKUP),
        (revenue_summary, _REVENUE_SUMMARY),
        (send_proposal, _SEND_PROPOSAL),
    )
    return [
        StructuredTool.from_function(func, name=func.__name__, description=description)
        for func, description in specs
    ]


def build_harness(config: HarnessConfig, model: BaseChatModel | None = None):
    """Assemble the agent. Does not read provider credentials or invoke the model."""
    from stages import (
        disable_general_purpose_delegate,
        parent_middleware,
        reviewer_subagent,
    )

    context = company_context(config.repo_root)
    disable_general_purpose_delegate()
    chosen = SilentModel() if model is None else model
    visible = tools_for_role(config)
    lookup = next(tool for tool in company_tools(config) if tool.name == "customer_brief")
    return create_deep_agent(
        model=chosen,
        tools=visible,
        system_prompt=str(context["agents_text"]),
        skills=list(context["skills"]),
        memory=list(context["memory"]),
        subagents=[reviewer_subagent(lookup, chosen)],
        middleware=parent_middleware(),
        backend=FilesystemBackend(root_dir=str(config.repo_root), virtual_mode=True),
    )
