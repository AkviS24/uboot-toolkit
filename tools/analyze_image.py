"""Command-line tool for analyzing firmware images."""
import argparse
from pathlib import Path

from uboot_toolkit.detector import detect_signatures
from uboot_toolkit.parser import parse_dtb_header


def analyze_image(image_path: Path) -> None:
    """Analyze a firmware image."""
    if not image_path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    size = image_path.stat().st_size

    print(f"File: {image_path}")
    print(f"Size: {size:,} bytes (0x{size:X})")

    with image_path.open("rb") as image_file:
        data = image_file.read()

    header = data[:64]
    print(f"First 64 bytes: {header.hex(' ')}")

    detections = detect_signatures(data)

    print("\n=== Detected Structures ===")

    if not detections:
        print("No known signatures found.")
        return
    for detection in detections:
        print(f"{detection.name}")
        print(f"  Offset: 0x{detection.offset:08X}")
        print(f"  Signature: {detection.signature.hex(' ')}")

        if detection.name == "Device Tree Blob (DTB)":
            dtb = parse_dtb_header(data, detection.offset)

            print(f" Total Size: {dtb.total_size:,} bytes")
            print(f" Structure Offset: 0x{dtb.structure_offset:08X}")
            print(f" Strings Offset: 0x{dtb.strings_offset:08X}")
            print(
                " Memory Reservation Offset: "
                f"0x{dtb.memory_reservation_offset:08X}"
            )
            print(f" Version: {dtb.version}")
            print(
                " Last Compatible Version: "
                f"{dtb.last_compatible_version}"
            )
            print(f" Boot CPU ID: 0x{dtb.boot_cpu_id:08X}")
            print(f" Structure Size: {dtb.structure_size:,} bytes")
            print(f" Strings Size: {dtb.strings_size:,} bytes")


def main() -> None:
    """Run the Command-Line interface."""
    parser = argparse.ArgumentParser(
        description="Analyze a firmware image..."
    )
    parser.add_argument(
        "image",
        type=Path,
        help="Path to the firmware image.",
    )

    args = parser.parse_args()
    analyze_image(args.image)

if __name__ == "__main__":
    main()