from uboot_toolkit.decoder import get_node_cell_sizes
from uboot_toolkit.structure import DtbNode, DtbProperty


def test_get_node_cell_sizes() -> None:
    """Read address and size cell counts from a DTB node."""

    node = DtbNode(
        name="parent",
        children=[],
        properties=[
            DtbProperty(
                name="#address-cells",
                value=b"\x00\x00\x00\x02",
            ),
            DtbProperty(
                name="#size-cells",
                value=b"\x00\x00\x00\x01",
            ),
        ],
    )

    result = get_node_cell_sizes(node)

    assert result == (2, 1)