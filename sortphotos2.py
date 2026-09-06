import os
import shutil
import argparse
from datetime import datetime

def organize_by_creation_date(src_folder, dst_folder, ignore_duplicates=True):
    if not os.path.isdir(src_folder):
        raise FileNotFoundError(f"Source folder does not exist: {src_folder}")

    # Ensure the destination exists
    os.makedirs(dst_folder, exist_ok=True)

    for root, dirs, files in os.walk(src_folder):
        for filename in files:
            src_path = os.path.join(root, filename)

            try:
                # Get Windows creation time
                stat_data = os.stat(src_path)
                creation_timestamp = stat_data.st_ctime
                creation_date = (datetime
                                 .fromtimestamp(creation_timestamp))

                # Build Year/Month folder structure
                year_folder = creation_date.strftime("%Y")
                month_folder = creation_date.strftime("%m")
                day_folder = creation_date.strftime("%d")
                foldertext = ""
                start = root.find(' ')
                end = len(root)
                if start == -1:  # some folder have context text after date and I want to preserve that
                    foldertext = ''
                else:
                    temp = root[start + 1:end]
                    foldertext = ' ' + temp.lstrip(' -')

                if src_path.split('\\')[1] > '2000' and src_path.split('\\')[1] < '3000':
                    templist = src_path.split('\\')
                    temp = '\\'.join(templist[1:3])
                    tempday = templist[3].split(' ')[0]
                    new_path = os.path.join(temp , tempday.repalace('-','_'))
                elif src_path.split('\\')[2] < year_folder:
                    templist = src_path.split('\\')
                    temp = '\\'.join(templist[2:4])
                    tempday = templist[4].split(' ')[0]
                    new_path = os.path.join(temp ,  tempday.repalace('-','_'))
                else:
                    new_path = os.path.join(year_path, year_folder + "_" + month_folder,year_folder + "_" + month_folder + "_" + day_folder)
                new_path = os.path.join(dst_folder, new_path)


                dir_path = new_path + foldertext

                os.makedirs(dir_path, exist_ok=True)
                if filename.split('.')[1] in ['lnk']:
                    continue
                dst_path = os.path.join(dir_path, filename)

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
        description="Organize files into Year/Month folders based on creation date."
    )

    parser.add_argument(
        "-s", "--source",
        required=True,
        help="Source directory."
    )

    parser.add_argument(
        "-d", "--destination",
        required=True,
        help="Destination directory."
    )

    parser.add_argument(
        "-i", "--ignore-duplicates",
        action="store_true",
        help="Skip files that already exist in the target folder."
    )

    args = parser.parse_args()

    organize_by_creation_date(
        src_folder=args.source,
        dst_folder=args.destination,
        ignore_duplicates=args.ignore_duplicates
    )


if __name__ == "__main__":
    main()
