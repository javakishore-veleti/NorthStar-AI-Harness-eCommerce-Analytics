from fastapi import APIRouter

from north_start_ecomm_mcp.domains.financials.api.objects_factory import RevenueSummaryApiFactory

router = APIRouter()
router.add_api_route(
    "/api/financials/revenue",
    RevenueSummaryApiFactory.get_revenue_summary_api().revenue_summary,
    methods=["POST"],
)
