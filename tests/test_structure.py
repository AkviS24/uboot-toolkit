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