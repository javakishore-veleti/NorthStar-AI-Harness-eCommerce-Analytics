from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

from north_start_ecomm_mcp.app.http_role import role_from_header
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx
from north_start_ecomm_mcp.domains.customer.facades.objects_factory import CustomerFacadeFactory
from north_start_ecomm_mcp.domains.customer.mcp_tools.interfaces import CustomerBriefTool

_DESCRIPTION = (
    "look up a customer's recorded goal and contact before answering or drafting. Cite the record id when the facts are used. The tool does not change data."
)


class CustomerBriefToolImpl(CustomerBriefTool, metaclass=Singleton):
    def customer_brief(self, ctx: CustomerCtx) -> CustomerCtx:
        headers = get_http_headers(include={"x-employee-role"})
        ctx.req.role = role_from_header(headers.get("x-employee-role"))
        return CustomerFacadeFactory.get_customer_facade().lookup(ctx)

    def register(self, server: FastMCP) -> None:
        server.tool(self.customer_brief, name="customer_brief", description=_DESCRIPTION)
