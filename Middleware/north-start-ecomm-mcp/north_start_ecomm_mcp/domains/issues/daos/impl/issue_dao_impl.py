from north_start_ecomm_mcp.common.database import DatabaseGateway
from north_start_ecomm_mcp.common.singleton import Singleton
from north_start_ecomm_mcp.domains.issues.daos.interfaces import IssueDao
from north_start_ecomm_mcp.domains.issues.dtos.domainCtx import IssueCtx
from north_start_ecomm_mcp.domains.issues.dtos.domainResp import IssueRecord

_BY_CUSTOMER = """
SELECT id, customer, symptom, owner
FROM issues
WHERE customer = ? COLLATE NOCASE
"""


class IssueDaoImpl(IssueDao, metaclass=Singleton):
    def find_by_customer(self, ctx: IssueCtx) -> IssueCtx:
        rows = DatabaseGateway().read(_BY_CUSTOMER, (ctx.req.customer,))
        ctx.resp.records = [
            IssueRecord(
                id=row["id"],
                customer=row["customer"],
                symptom=row["symptom"],
                owner=row["owner"],
            )
            for row in rows
        ]
        return ctx
