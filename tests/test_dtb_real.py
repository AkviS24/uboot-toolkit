from pathlib import Path

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