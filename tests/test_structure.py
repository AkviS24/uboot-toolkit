from uboot_toolkit.structure import (
    DtbNode,
    FDT_BEGIN_NODE,
    FDT_END_NODE,
    FDT_PROP,
    FDT_END,
    build_dtb_tree,
    parse_structure,
)


def test_parse_structure_tokens():
    data = (
        b"\x00\x00\x00\x01"  # FDT_BEGIN_NODE
        b"root\x00\x00\x00\x00"
        b"\x00\x00\x00\x02"  # FDT_END_NODE
        b"\x00\x00\x00\x09"  # FDT_END
    )

    tokens = parse_structure(data, 0, len(data))

    assert [token.token for token in tokens] == [
        FDT_BEGIN_NODE,
        FDT_END_NODE,
        FDT_END,
    ]


def test_parse_property_token():
    property_data = b"ABCD"

    data = (
        b"\x00\x00\x00\x03"  # FDT_PROP
        + len(property_data).to_bytes(4, "big")
        + b"\x00\x00\x00\x00"
        + property_data
        + b"\x00\x00\x00\x09"  # FDT_END
    )

    tokens = parse_structure(data, 0, len(data))

    assert [token.token for token in tokens] == [
        FDT_PROP,
        FDT_END,
    ]


def test_parse_empty_structure():
    data = b"\x00\x00\x00\x09"

    tokens = parse_structure(data, 0, len(data))

    assert len(tokens) == 1
    assert tokens[0].name == "END"


def test_structure_end_matches_calculated_boundary() -> None:
    """Ensure FDT_END is the final 4-byte token of the structure block."""
    data = (
        b"\x00\x00\x00\x01"  # FDT_BEGIN_NODE
        b"\x00\x00\x00\x00"  # Empty node name + padding
        b"\x00\x00\x00\x09"  # FDT_END
    )

    tokens = parse_structure(data, 0, len(data))

    assert tokens[-1].name == "END"
    assert tokens[-1].offset + 4 == len(data)


def test_parse_structure_reads_node_name():
    data = (
        b"\x00\x00\x00\x01"  # FDT_BEGIN_NODE
        b"root\x00\x00\x00\x00"
        b"\x00\x00\x00\x09"  # FDT_END
    )

    tokens = parse_structure(data, 0, len(data))

    assert tokens[0].name == "BEGIN_NODE"
    assert tokens[0].node_name == "root"


def test_parse_property_metadata():
    property_data = b"ABCD"
    property_name_offset = 0x10

    data = (
        b"\x00\x00\x00\x03"  # FDT_PROP
        + len(property_data).to_bytes(4, "big")
        + property_name_offset.to_bytes(4, "big")
        + property_data
        + b"\x00\x00\x00\x09"  # FDT_END
    )

    tokens = parse_structure(data, 0, len(data))

    property_token = tokens[0]

    assert property_token.name == "PROP"
    assert property_token.property_length == 4
    assert property_token.property_name_offset == 0x10
    assert property_token.property_value == b"ABCD"



def test_dtb_node_creation():
    """Create a DTB node with children and properties."""
    child = DtbNode(
        name="chosen",
        children=[],
        properties=[],
    )

    root = DtbNode(
        name="",
        children=[child],
        properties=[],
    )

    assert root.name == ""
    assert len(root.children) == 1
    assert root.children[0].name == "chosen"
    assert root.properties == []


def test_build_dtb_tree():
    """Build a node tree from structure tokens."""
    data = (
        b"\x00\x00\x00\x01"  # FDT_BEGIN_NODE
        b"\x00\x00\x00\x00"  # root name + padding
        b"\x00\x00\x00\x01"  # FDT_BEGIN_NODE
        b"chosen\x00\x00"     # chosen + padding
        b"\x00\x00\x00\x02"  # FDT_END_NODE
        b"\x00\x00\x00\x02"  # FDT_END_NODE
        b"\x00\x00\x00\x09"  # FDT_END
    )

    tokens = parse_structure(data, 0, len(data))
    root = build_dtb_tree(tokens)

    assert root.name == ""
    assert len(root.children) == 1
    assert root.children[0].name == "chosen"



def test_build_dtb_tree_assigns_properties():
    """Assign properties to the node they belong to."""
    property_data = b"ABCD"

    data = (
        b"\x00\x00\x00\x01"  # FDT_BEGIN_NODE
        b"\x00\x00\x00\x00"  # root name + padding
        b"\x00\x00\x00\x03"  # FDT_PROP
        + len(property_data).to_bytes(4, "big")
        + b"\x00\x00\x00\x00"  # property name offset
        + property_data
        + b"\x00\x00\x00\x02"  # FDT_END_NODE
        b"\x00\x00\x00\x09"  # FDT_END
    )

    tokens = parse_structure(data, 0, len(data))
    root = build_dtb_tree(tokens)

    assert len(root.properties) == 1
    assert root.properties[0].property_length == 4
    assert root.properties[0].property_name_offset == 0
    assert root.properties[0].property_value == b"ABCD"



def test_build_dtb_tree_assigns_nested_properties():
    """Assign a property to the correct nested node."""
    property_data = b"boot"

    data = (
        b"\x00\x00\x00\x01"  # FDT_BEGIN_NODE
        b"\x00\x00\x00\x00"  # root name + padding
        b"\x00\x00\x00\x01"  # FDT_BEGIN_NODE
        b"chosen\x00\x00"     # chosen + padding
        b"\x00\x00\x00\x03"  # FDT_PROP
        + len(property_data).to_bytes(4, "big")
        + b"\x00\x00\x00\x00"  # property name offset
        + property_data
        + b"\x00\x00\x00\x02"  # end chosen
        b"\x00\x00\x00\x02"    # end root
        b"\x00\x00\x00\x09"    # FDT_END
    )

    tokens = parse_structure(data, 0, len(data))
    root = build_dtb_tree(tokens)

    assert root.properties == []
    assert len(root.children) == 1

    chosen = root.children[0]

    assert chosen.name == "chosen"
    assert len(chosen.properties) == 1
    assert chosen.properties[0].property_value == b"boot"