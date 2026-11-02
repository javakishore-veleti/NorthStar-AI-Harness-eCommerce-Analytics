from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx


class LookupCustomerTask(ABC):
    @abstractmethod
    def execute(self, ctx: CustomerCtx) -> CustomerCtx:
        """Run the task. The only argument is the domain context."""
