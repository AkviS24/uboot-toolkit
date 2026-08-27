from uboot_toolkit.structure import (
    FDT_BEGIN_NODE,
    FDT_END_NODE,
    FDT_PROP,
    FDT_END,
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