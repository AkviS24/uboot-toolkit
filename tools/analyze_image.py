from pathlib import Path
from uboot_toolkit.detector import detect_signatures
import argparse

def analyze_image(image_path: Path) -> None:
    """Display Basic Informations about a firmware image File."""
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


def main() -> None:
    """Command-Line entry Point"""
    parser = argparse.ArgumentParser(
        description="Analyze U-Boot and firmware images..."
    )
    parser.add_argument(
        "image",
        type=Path,
        help="Path to the firmware image.",
    )

    args = parser.parse_args()
    try:
        analyze_image(args.image)
    except FileNotFoundError as error:
        parser.error(str(error))

if __name__ == "__main__":
    main()