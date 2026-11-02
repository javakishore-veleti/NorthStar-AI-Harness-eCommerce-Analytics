from north_start_ecomm_mcp.domains.issues.daos.impl.issue_dao_impl import IssueDaoImpl
from north_start_ecomm_mcp.domains.issues.daos.interfaces import IssueDao


class IssueDaoFactory:
    @staticmethod
    def get_issue_dao() -> IssueDao:
        return IssueDaoImpl()
