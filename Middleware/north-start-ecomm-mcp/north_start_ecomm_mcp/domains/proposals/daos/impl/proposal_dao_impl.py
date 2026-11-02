import hashlib

from north_start_ecomm_mcp.common.database import DatabaseGateway
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.proposals.daos.interfaces import ProposalDao
from north_start_ecomm_mcp.domains.proposals.dtos.domainCtx import ProposalCtx

_INSERT = "INSERT OR IGNORE INTO outbox (id, customer, body) VALUES (?, ?, ?)"


class ProposalDaoImpl(ProposalDao, metaclass=Singleton):
    def insert_outbox(self, ctx: ProposalCtx) -> ProposalCtx:
        customer = ctx.req.customer
        body = ctx.req.body
        receipt = hashlib.sha256(f"{customer}\0{body}".encode()).hexdigest()[:16]
        DatabaseGateway().write(_INSERT, (receipt, customer, body))
        ctx.resp.status = "simulated_send"
        ctx.resp.receipt = receipt
        ctx.resp.customer = customer
        return ctx
