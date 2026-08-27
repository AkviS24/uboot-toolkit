"""Tests for binary structure parsers."""

import pytest

from uboot_toolkit.structure import (
    DtbNode,
    DtbProperty,
    FDT_BEGIN_NODE,
    FDT_PROP,
    StructureToken,
)

from uboot_toolkit.parser import (
    build_dtb_property,
    convert_dtb_properties,
    get_dtb_structure_bounds,
    parse_dtb,
    parse_dtb_header,
    resolve_dtb_string,
    resolve_property_name,
)

def test_parse_dtb_header() -> None:
    """Parse a valid DTB header."""
    data = bytes.fromhex(
        "D00DFEED"
        "00000A00"
        "00000048"
        "00000808"
        "00000028"
        "00000011"
        "00000010"
        "00000000"
        "000000CD"
        "000007C0"
    )

    header = parse_dtb_header(data)

    assert header.magic == 0xD00DFEED
    assert header.total_size == 2560
    assert header.structure_offset == 0x48
    assert header.strings_offset == 0x808
    assert header.memory_reservation_offset == 0x28
    assert header.version == 17
    assert header.last_compatible_version == 16
    assert header.boot_cpu_id == 0
    assert header.structure_size == 1984
    assert header.strings_size == 205


def test_parse_dtb_header_at_offset() -> None:
    """Parse a DTB header at a non-zero offset."""
    header_data = bytes.fromhex(
        "D00DFEED"
        "00000A00"
        "00000048"
        "00000808"
        "00000028"
        "00000011"
        "00000010"
        "00000000"
        "000000CD"
        "000007C0"
    )

    data = b"\x00" * 10 + header_data

    header = parse_dtb_header(data, offset=10)

    assert header.magic == 0xD00DFEED
    assert header.total_size == 2560


def test_parse_invalid_dtb_magic() -> None:
    """Reject data with an invalid DTB magic."""
    data = b"\x00" * 40

    with pytest.raises(ValueError, match="Invalid DTB magic"):
        parse_dtb_header(data)


def test_parse_incomplete_dtb_header() -> None:
    """Reject data shorter than a DTB header."""
    data = b"\xD0\x0D\xFE\xED"

    with pytest.raises(ValueError, match="Not enough data"):
        parse_dtb_header(data)

def test_get_dtb_structure_bounds() -> None:
    """Calculate absolute DTB structure boundaries."""
    data = bytes.fromhex(
        "D00DFEED"
        "00000A00"
        "00000048"
        "00000808"
        "00000028"
        "00000011"
        "00000010"
        "00000000"
        "000000CD"
        "000007C0"
    )

    header = parse_dtb_header(data)

    start, end = get_dtb_structure_bounds(header)

    assert start == 0x48
    assert end == 0x808


def test_resolve_dtb_string() -> None:
    """Resolve a null-terminated string from the DTB strings block."""
    strings = b"compatible\x00model\x00bootargs\x00"

    data = b"\x00" * 0x20 + strings

    result = resolve_dtb_string(
        data=data,
        strings_offset=0x20,
        strings_size=len(strings),
        name_offset=0,
    )

    assert result == "compatible"


def test_resolve_dtb_string_at_offset() -> None:
    """Resolve a string using an offset inside the strings block."""
    strings = b"compatible\x00model\x00bootargs\x00"

    data = b"\x00" * 0x20 + strings

    result = resolve_dtb_string(
        data=data,
        strings_offset=0x20,
        strings_size=len(strings),
        name_offset=11,
    )

    assert result == "model"


def test_resolve_property_name() -> None:
    """Resolve a property token name from the DTB strings block."""
    strings = b"compatible\x00model\x00bootargs\x00"

    data = b"\x00" * 0x20 + strings

    token = StructureToken(
        offset=0,
        token=FDT_PROP,
        name="PROP",
        property_length=4,
        property_name_offset=0,
        property_value=b"ABCD",
    )

    result = resolve_property_name(
        token=token,
        data=data,
        strings_offset=0x20,
        strings_size=len(strings),
    )

    assert result == "compatible"


def test_build_dtb_property():
    """Convert a property token into a DtbProperty."""
    strings = b"compatible\x00model\x00"

    data = b"\x00" * 0x20 + strings

    token = StructureToken(
        offset=0,
        token=FDT_PROP,
        name="PROP",
        property_length=15,
        property_name_offset=0,
        property_value=b"rockchip,rk3566",
    )

    property_item = build_dtb_property(
        token=token,
        data=data,
        strings_offset=0x20,
        strings_size=len(strings),
    )

    assert property_item.name == "compatible"
    assert property_item.value == b"rockchip,rk3566"


def test_build_dtb_property_rejects_non_property_token():
    """Reject a token that is not an FDT property token."""
    token = StructureToken(
        offset=0,
        token=FDT_BEGIN_NODE,
        name="BEGIN_NODE",
        node_name="root",
    )

    with pytest.raises(ValueError, match="Token is not a property token"):
        build_dtb_property(
            token=token,
            data=b"",
            strings_offset=0,
            strings_size=0,
        )



def test_convert_dtb_properties():
    """Convert property tokens in a DTB node into DtbProperty objects."""
    strings = b"compatible\x00"
    data = b"\x00" * 0x20 + strings

    token = StructureToken(
        offset=0,
        token=FDT_PROP,
        name="PROP",
        property_length=15,
        property_name_offset=0,
        property_value=b"rockchip,rk3566",
    )

    root = DtbNode(
        name="",
        properties=[token],
        children=[],
    )

    result = convert_dtb_properties(
        node=root,
        data=data,
        strings_offset=0x20,
        strings_size=len(strings),
    )

    assert result is root
    assert len(result.properties) == 1

    assert isinstance(result.properties[0], DtbProperty)
    assert result.properties[0].name == "compatible"
    assert result.properties[0].value == b"rockchip,rk3566"



def test_convert_dtb_properties_recursively():
    """Convert properties in child nodes recursively."""
    strings = b"bootargs\x00"
    data = b"\x00" * 0x20 + strings

    token = StructureToken(
        offset=0,
        token=FDT_PROP,
        name="PROP",
        property_length=4,
        property_name_offset=0,
        property_value=b"boot",
    )

    child = DtbNode(
        name="chosen",
        properties=[token],
        children=[],
    )

    root = DtbNode(
        name="",
        properties=[],
        children=[child],
    )

    result = convert_dtb_properties(
        node=root,
        data=data,
        strings_offset=0x20,
        strings_size=len(strings),
    )

    chosen = result.children[0]

    assert len(result.properties) == 0
    assert len(chosen.properties) == 1

    assert isinstance(chosen.properties[0], DtbProperty)
    assert chosen.properties[0].name == "bootargs"
    assert chosen.properties[0].value == b"boot"


def test_convert_multiple_dtb_properties():
    """Convert multiple properties belonging to the same node."""
    strings = b"compatible\x00model\x00"
    data = b"\x00" * 0x20 + strings

    compatible_token = StructureToken(
        offset=0,
        token=FDT_PROP,
        name="PROP",
        property_length=15,
        property_name_offset=0,
        property_value=b"rockchip,rk3566",
    )

    model_token = StructureToken(
        offset=0,
        token=FDT_PROP,
        name="PROP",
        property_length=8,
        property_name_offset=11,
        property_value=b"T95 Plus",
    )

    root = DtbNode(
        name="",
        properties=[
            compatible_token,
            model_token,
        ],
        children=[],
    )

    result = convert_dtb_properties(
        node=root,
        data=data,
        strings_offset=0x20,
        strings_size=len(strings),
    )

    assert len(result.properties) == 2

    assert isinstance(result.properties[0], DtbProperty)
    assert result.properties[0].name == "compatible"
    assert result.properties[0].value == b"rockchip,rk3566"

    assert isinstance(result.properties[1], DtbProperty)
    assert result.properties[1].name == "model"
    assert result.properties[1].value == b"T95 Plus"


def test_parse_dtb_end_to_end() -> None:
    """Parse a minimal DTB from raw bytes to a structured tree."""

    strings = b"compatible\x00"

    structure = (
        b"\x00\x00\x00\x01"          # FDT_BEGIN_NODE
        b"\x00\x00\x00\x00"          # empty root node name + padding
        b"\x00\x00\x00\x03"          # FDT_PROP
        b"\x00\x00\x00\x0F"          # property length = 15
        b"\x00\x00\x00\x00"          # name offset = 0
        b"rockchip,rk3566"            # property value
        b"\x00"                   # padding
        b"\x00\x00\x00\x02"          # FDT_END_NODE
        b"\x00\x00\x00\x09"          # FDT_END
    )

    structure_offset = 0x28
    strings_offset = structure_offset + len(structure)

    header = (
        b"\xD0\x0D\xFE\xED"                           # magic
        + (strings_offset + len(strings)).to_bytes(4, "big")
        + structure_offset.to_bytes(4, "big")
        + strings_offset.to_bytes(4, "big")
        + (0x28).to_bytes(4, "big")                  # memory reservation
        + (17).to_bytes(4, "big")                    # version
        + (16).to_bytes(4, "big")                    # last compatible
        + (0).to_bytes(4, "big")                     # boot CPU
        + len(strings).to_bytes(4, "big")           # strings size
        + len(structure).to_bytes(4, "big")         # structure size
    )

    data = header + structure + strings

    result = parse_dtb(data)

    assert result.name == ""
    assert len(result.properties) == 1

    property_item = result.properties[0]

    assert property_item.name == "compatible"
    assert property_item.value == b"rockchip,rk3566"


def test_parse_dtb_end_to_end_with_child_node() -> None:
    """Parse a DTB with nested child nodes from raw bytes."""

    strings = (
        b"compatible\x00"
        b"status\x00"
    )

    structure = (
        # /
        b"\x00\x00\x00\x01"          # FDT_BEGIN_NODE
        b"\x00\x00\x00\x00"          # empty root name + padding

        # compatible = "rockchip,rk3566"
        b"\x00\x00\x00\x03"          # FDT_PROP
        b"\x00\x00\x00\x0F"          # property length = 15
        b"\x00\x00\x00\x00"          # name offset = 0
        b"rockchip,rk3566"            # property value
        b"\x00"                       # padding

        # soc
        b"\x00\x00\x00\x01"          # FDT_BEGIN_NODE
        b"soc\x00"                    # node name

        # serial@fe650000
        b"\x00\x00\x00\x01"          # FDT_BEGIN_NODE
        b"serial@fe650000\x00"        # node name

        # status = "okay"
        b"\x00\x00\x00\x03"          # FDT_PROP
        b"\x00\x00\x00\x05"          # property length = 5
        b"\x00\x00\x00\x0B"          # name offset = 11
        b"okay\x00"                   # property value
        b"\x00\x00\x00"               # padding

        b"\x00\x00\x00\x02"          # FDT_END_NODE serial
        b"\x00\x00\x00\x02"          # FDT_END_NODE soc
        b"\x00\x00\x00\x02"          # FDT_END_NODE root
        b"\x00\x00\x00\x09"          # FDT_END
    )

    structure_offset = 0x28
    strings_offset = structure_offset + len(structure)

    header = (
        b"\xD0\x0D\xFE\xED"
        + (strings_offset + len(strings)).to_bytes(4, "big")
        + structure_offset.to_bytes(4, "big")
        + strings_offset.to_bytes(4, "big")
        + (0x28).to_bytes(4, "big")
        + (17).to_bytes(4, "big")
        + (16).to_bytes(4, "big")
        + (0).to_bytes(4, "big")
        + len(strings).to_bytes(4, "big")
        + len(structure).to_bytes(4, "big")
    )

    data = header + structure + strings

    result = parse_dtb(data)

    assert result.name == ""
    assert len(result.properties) == 1
    assert result.properties[0].name == "compatible"
    assert result.properties[0].value == b"rockchip,rk3566"

    assert len(result.children) == 1

    soc = result.children[0]

    assert soc.name == "soc"
    assert len(soc.properties) == 0
    assert len(soc.children) == 1

    serial = soc.children[0]

    assert serial.name == "serial@fe650000"
    assert len(serial.properties) == 1
    assert serial.properties[0].name == "status"
    assert serial.properties[0].value == b"okay\x00"