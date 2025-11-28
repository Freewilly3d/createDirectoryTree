import os
import shutil
import argparse
from datetime import datetime

def organize_by_creation_date(src_folder, dst_folder, date_format, ignore_duplicates=True):
    os.makedirs(dst_folder, exist_ok=True)

    for root, dirs, files in os.walk(src_folder):
        for filename in files:
            src_path = os.path.join(root, filename)

            try:
                # Get Windows creation time
                creation_timestamp = os.path.getctime(src_path)
                creation_date = datetime.fromtimestamp(creation_timestamp)

                # Use strftime format string
                folder_name = creation_date.strftime(date_format)

                target_folder = os.path.join(dst_folder, folder_name)
                os.makedirs(target_folder, exist_ok=True)

                dst_path = os.path.join(target_folder, filename)

                # Duplicate check
                if ignore_duplicates and os.path.exists(dst_path):
                    print(f"Duplicate skipped: {dst_path}")
                    continue

                shutil.copy2(src_path, dst_path)
                print(f"Copied: {src_path} → {dst_path}")

            except Exception as e:
                print(f"Error processing {src_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Organize files into folders based on creation date."
    )

    parser.add_argument("source", help="Source directory.")
    parser.add_argument("destination", help="Destination directory.")

    parser.add_argument(
        "--date-format",
        default="%Y_%m",
        help=(
            "strftime-compatible folder name format. "
            'Example: "%Y_%m", "%Y-%m-%d", "%Y", "%b_%Y". '
            "Default is %Y_%m"
        )
    )

    parser.add_argument(
        "--ignore-duplicates",
        action="store_true",
        help="Skip files that already exist in the target folder.",
    )

    args = parser.parse_args()

    organize_by_creation_date(
        src_folder=args.source,
        dst_folder=args.destination,
        date_format=args.date_format,
        ignore_duplicates=args.ignore_duplicates
    )


if __name__ == "__main__":
    main()
