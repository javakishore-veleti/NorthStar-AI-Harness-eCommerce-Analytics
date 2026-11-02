from fastapi import APIRouter

from north_start_ecomm_mcp.domains.issues.api.objects_factory import IssueLookupApiFactory

router = APIRouter()
router.add_api_route(
    "/api/issues/lookup",
    IssueLookupApiFactory.get_issue_lookup_api().issue_lookup,
    methods=["POST"],
)
