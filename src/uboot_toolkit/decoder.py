"""Decode Device Tree Blob property values."""

from uboot_toolkit.structure import DtbNode, DtbProperty


def decode_dtb_property(value: bytes):
    """Decode a DTB property value into a useful Python representation."""

    if not value:
        return None

    if value.endswith(b"\x00"):
        strings = value.rstrip(b"\x00").split(b"\x00")

        if len(strings) > 1:
            return [
                item.decode("ascii", errors="replace")
                for item in strings
            ]

        return value.rstrip(b"\x00").decode(
            "ascii",
            errors="replace",
        )

    if len(value) % 4 == 0:
        cells = [
            int.from_bytes(
                value[index:index + 4],
                "big",
            )
            for index in range(0, len(value), 4)
        ]

        if len(cells) == 1:
            return cells[0]

        return cells

    return value


def decode_reg(
    value: bytes,
    address_cells: int,
    size_cells: int,
) -> list[dict[str, int]]:
    """Decode a DTB reg property into address/size entries."""

    if address_cells < 1:
        raise ValueError("address_cells must be at least 1.")

    if size_cells < 1:
        raise ValueError("size_cells must be at least 1.")

    entry_cells = address_cells + size_cells
    entry_size = entry_cells * 4

    if len(value) % entry_size != 0:
        raise ValueError(
            "reg property length is not a multiple of the entry size."
        )

    entries = []

    for offset in range(0, len(value), entry_size):
        address = 0

        for index in range(address_cells):
            cell_start = offset + index * 4
            cell = int.from_bytes(
                value[cell_start:cell_start + 4],
                "big",
            )
            address = (address << 32) | cell

        size = 0

        size_offset = offset + address_cells * 4

        for index in range(size_cells):
            cell_start = size_offset + index * 4
            cell = int.from_bytes(
                value[cell_start:cell_start + 4],
                "big",
            )
            size = (size << 32) | cell

        entries.append(
            {
                "address": address,
                "size": size,
            }
        )

    return entries


def get_node_cell_sizes(
    node: DtbNode,
) -> tuple[int, int]:
    """Return address-cell and size-cell counts from a DTB node."""

    address_cells = 2
    size_cells = 1

    for prop in node.properties:
        if not isinstance(prop, DtbProperty):
            continue

        if prop.name == "#address-cells":
            if len(prop.value) != 4:
                raise ValueError(
                    "#address-cells must contain one 32-bit cell."
                )

            address_cells = int.from_bytes(
                prop.value,
                "big",
            )

        elif prop.name == "#size-cells":
            if len(prop.value) != 4:
                raise ValueError(
                    "#size-cells must contain one 32-bit cell."
                )

            size_cells = int.from_bytes(
                prop.value,
                "big",
            )

    if address_cells < 1:
        raise ValueError("#address-cells must be at least 1.")

    if size_cells < 1:
        raise ValueError("#size-cells must be at least 1.")

    return address_cells, size_cells