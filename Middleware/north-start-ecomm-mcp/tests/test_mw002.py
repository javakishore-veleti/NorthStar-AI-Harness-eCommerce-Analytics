import ast
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
PACKAGE = PROJECT / "north_start_ecomm_mcp"


class SingletonTests(unittest.TestCase):
    def test_two_constructions_return_the_same_instance(self) -> None:
        from north_start_ecomm_mcp.common.singleton import Singleton

        class Box(metaclass=Singleton):
            def __init__(self) -> None:
                self.marker = object()

        self.assertIs(Box(), Box())

    def test_subclasses_do_not_share_an_instance(self) -> None:
        from north_start_ecomm_mcp.common.singleton import Singleton

        class Left(metaclass=Singleton):
            pass

        class Right(metaclass=Singleton):
            pass

        self.assertIsNot(Left(), Right())
        Left.clear()
        Right.clear()

    def tearDown(self) -> None:
        from north_start_ecomm_mcp.common.singleton import Singleton

        Singleton._instances.clear()


class ImportAuditTests(unittest.TestCase):
    def test_audit_passes_on_the_current_tree_with_empty_domains(self) -> None:
        from tests.closed_layer_audit import audit_package

        domains = PACKAGE / "domains"
        self.assertFalse(domains.exists())
        self.assertEqual(audit_package(PACKAGE), [])

    def test_proposal_facade_impl_may_import_customer_facade_factory(self) -> None:
        from tests.closed_layer_audit import violations_for

        relative = Path(
            "domains/proposals/facades/proposal_facade/proposal_facade_impl.py"
        )
        source = (
            "from north_start_ecomm_mcp.domains.customer.facades.objects_factory "
            "import CustomerFacadeFactory\n"
        )
        self.assertEqual(violations_for(relative, source), [])

    def test_proposal_facade_impl_still_cannot_import_a_dao(self) -> None:
        from tests.closed_layer_audit import violations_for

        relative = Path(
            "domains/proposals/facades/proposal_facade/proposal_facade_impl.py"
        )
        source = "from north_start_ecomm_mcp.domains.customer.daos.objects_factory import CustomerDaoFactory\n"
        self.assertTrue(violations_for(relative, source))

    def test_task_cannot_import_customer_facade_factory(self) -> None:
        from tests.closed_layer_audit import violations_for

        relative = Path(
            "domains/proposals/facades/proposal_facade/tasks/send_proposal_task.py"
        )
        source = (
            "from north_start_ecomm_mcp.domains.customer.facades.objects_factory "
            "import CustomerFacadeFactory\n"
        )
        self.assertTrue(violations_for(relative, source))

    def test_presentation_cannot_import_database(self) -> None:
        from tests.closed_layer_audit import violations_for

        relative = Path("domains/customer/api/brief.py")
        source = "from north_start_ecomm_mcp.common.database import DatabaseGateway\n"
        self.assertTrue(violations_for(relative, source))

    def test_dao_cannot_import_presentation(self) -> None:
        from tests.closed_layer_audit import violations_for

        relative = Path("domains/customer/daos/impl/customer_dao_impl.py")
        source = "from north_start_ecomm_mcp.domains.customer.api import brief\n"
        self.assertTrue(violations_for(relative, source))

    def test_sources_parse(self) -> None:
        for path in PACKAGE.rglob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"))
