from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx


class CustomerDao(ABC):
    @abstractmethod
    def find_by_name(self, ctx: CustomerCtx) -> CustomerCtx:
        """Read customers by ctx.req.customer. The role is not a filter."""
