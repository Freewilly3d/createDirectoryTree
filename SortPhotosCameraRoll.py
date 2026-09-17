import os
import shutil
import argparse
from datetime import datetime
from PIL import Image

def get_date_taken(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                # Tag 36867 is DateTimeOriginal
                date_taken = exif_data.get(36867)
                if date_taken:
                    # Format is typically 'YYYY:MM:DD HH:MM:SS'
                    return datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Error: {e}")
    return None

def organize_by_creation_date(src_folder, dst_folder, ignore_duplicates=True,print_debug=False):
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
                w_year_folder = creation_date.strftime("%Y")
                w_month_folder = creation_date.strftime("%m")
                w_day_folder = creation_date.strftime("%d")

                date_obj = get_date_taken(src_path)
                temp = src_path.split('\\')
                x = len(temp)
                if len(temp) == 5:
                    temp2 = temp[4].split('_')
                    pic_date = datetime.strptime(temp2[0], '%Y%m%d')
                elif len(temp) == 4:
                    temp2 = temp[3].split('_')
                    pic_date = datetime.strptime(temp2[0], '%Y%m%d')
                else:
                    pic_date = None
                # Build Year/Month folder structure
                if date_obj != None and creation_date > date_obj and pic_date.date() >= date_obj.date():

                    year_folder = date_obj.strftime("%Y")
                    month_folder = date_obj.strftime("%m")
                    day_folder = date_obj.strftime("%d")
                    new_path = os.path.join(year_folder, year_folder + "_" + month_folder,
                                            year_folder + "_" + month_folder + "_" + day_folder)
                    if print_debug:
                        print(f"Date taken: {new_path}")

                elif pic_date.date() < creation_date.date():
                    year_folder = pic_date.strftime("%Y")
                    month_folder = pic_date.strftime("%m")
                    day_folder = pic_date.strftime("%d")

                else:
                    year_folder = creation_date.strftime("%Y")
                    month_folder = creation_date.strftime("%m")
                    day_folder = creation_date.strftime("%d")
                new_path = os.path.join(year_folder, year_folder + "_" + month_folder,
                                                year_folder + "_" + month_folder + "_" + day_folder)
                if print_debug:
                    print(f"Date Taken {date_obj}")
                    print(f"Date From file Name {pic_date})")
                    print(f"Date of file {creation_date}")


                foldertext = ""
#                start = root.find(' ')
#                end = len(root)
#                if start == -1:  # some folder have context text after date and I want to preserve that
#                    foldertext = ''
#                else:
#                    temp = root[start + 1:end]
#                    foldertext = ' ' + temp.lstrip(' -')


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
                #original_stat = os.stat(src_path)
                #os.utime(dst_path, (original_stat.st_atime, original_stat.st_mtime))
                if print_debug:
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
        "-p", "--print-debug",
        action="store_true",
        help="printed Debug."
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
        ignore_duplicates=args.ignore_duplicates,
        print_debug = args.print_debug
    )


if __name__ == "__main__":
    main()
