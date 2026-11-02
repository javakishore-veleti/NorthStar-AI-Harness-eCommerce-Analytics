from fastapi import APIRouter

from north_start_ecomm_mcp.domains.proposals.api.objects_factory import SendProposalApiFactory

router = APIRouter()
router.add_api_route(
    "/api/proposals/send",
    SendProposalApiFactory.get_send_proposal_api().send_proposal,
    methods=["POST"],
)
