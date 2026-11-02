from north_start_ecomm_mcp.common.database import DatabaseGateway
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.customer.daos.interfaces import CustomerDao
from north_start_ecomm_mcp.domains.customer.dtos.domainCtx import CustomerCtx
from north_start_ecomm_mcp.domains.customer.dtos.domainResp import CustomerRecord

_BY_NAME = """
SELECT id, name, need, contact
FROM customers
WHERE name = ? COLLATE NOCASE
"""


class CustomerDaoImpl(CustomerDao, metaclass=Singleton):
    def find_by_name(self, ctx: CustomerCtx) -> CustomerCtx:
        rows = DatabaseGateway().read(_BY_NAME, (ctx.req.customer,))
        ctx.resp.records = [
            CustomerRecord(
                id=row["id"],
                name=row["name"],
                need=row["need"],
                contact=row["contact"],
            )
            for row in rows
        ]
        return ctx
