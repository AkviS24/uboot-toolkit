"""Decode Device Tree Blob property values."""


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