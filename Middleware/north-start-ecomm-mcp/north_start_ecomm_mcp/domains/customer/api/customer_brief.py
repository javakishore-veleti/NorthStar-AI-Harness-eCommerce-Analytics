from fastapi import APIRouter

from north_start_ecomm_mcp.domains.customer.api.objects_factory import CustomerBriefApiFactory

router = APIRouter()
router.add_api_route(
    "/api/customer/brief",
    CustomerBriefApiFactory.get_customer_brief_api().customer_brief,
    methods=["POST"],
)
