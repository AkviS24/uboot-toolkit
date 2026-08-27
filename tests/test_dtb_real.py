from pathlib import Path

from uboot_toolkit.decoder import decode_dtb_property
from uboot_toolkit.parser import parse_dtb
from uboot_toolkit.structure import DtbNode, DtbProperty


DTB_PATH = Path(r"C:\Tools\platform-tools\uboot_dtb_large.dtb")


def test_parse_real_dtb() -> None:
    """Parse the real extracted DTB and verify its tree structure."""

    data = DTB_PATH.read_bytes()

    root = parse_dtb(data)

    assert isinstance(root, DtbNode)
    assert root.name == ""

    assert root.properties
    assert root.children


def test_real_dtb_contains_named_properties() -> None:
    """Verify that DTB property names are resolved correctly."""

    data = DTB_PATH.read_bytes()

    root = parse_dtb(data)

    properties = {
        prop.name: prop.value
        for prop in root.properties
        if isinstance(prop, DtbProperty)
    }

    assert properties


def test_real_dtb_print_root_properties() -> None:
    """Print the resolved root properties of the real DTB."""

    data = DTB_PATH.read_bytes()
    root = parse_dtb(data)

    print("\nReal DTB root properties:")

    for prop in root.properties:
        if isinstance(prop, DtbProperty):
            print(f"  {prop.name}: {prop.value!r}")


def test_real_dtb_print_tree() -> None:
    """Print the node hierarchy of the real DTB."""

    data = DTB_PATH.read_bytes()
    root = parse_dtb(data)

    def print_node(node: DtbNode, depth: int = 0) -> None:
        indent = "  " * depth
        print(f"{indent}{node.name or '/'}")

        for prop in node.properties:
            if isinstance(prop, DtbProperty):
                print(f"{indent}  [P] {prop.name}")

        for child in node.children:
            print_node(child, depth + 1)

    print("\nReal DTB tree:")
    print_node(root)


def test_real_dtb_property_values_can_be_decoded() -> None:
    """Decode selected properties from the real DTB."""

    data = DTB_PATH.read_bytes()
    root = parse_dtb(data)

    properties = {
        prop.name: prop.value
        for prop in root.properties
        if isinstance(prop, DtbProperty)
    }

    assert decode_dtb_property(
        properties["compatible"]
    ) == [
        "rockchip,rk3568-evb",
        "rockchip,rk3568",
    ]

    assert decode_dtb_property(
        properties["model"]
    ) == "Rockchip RK3568 Evaluation Board"

    assert decode_dtb_property(
        properties["#address-cells"]
    ) == 2

    assert decode_dtb_property(
        properties["#size-cells"]
    ) == 2