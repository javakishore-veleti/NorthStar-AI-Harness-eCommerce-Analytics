from abc import ABC, abstractmethod

from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx


class CustomerFacade(ABC):
    @abstractmethod
    def lookup(self, ctx: CustomerCtx) -> CustomerCtx:
        """Look up a customer. The only argument is the domain context."""
