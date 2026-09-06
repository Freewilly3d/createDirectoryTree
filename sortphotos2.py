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
                w_year_folder = creation_date.strftime("%Y")
                w_month_folder = creation_date.strftime("%m")
                w_day_folder = creation_date.strftime("%d")

                date_obj = get_date_taken(src_path)
                temp = src_path.split('\\')
                if temp[1] > '2000' and temp[1] < '3000':
                    temp2 = temp[3].replace('-','_')
                elif temp[0] > '2000' and temp[1] < '3000':
                    temp2 = temp[2].replace('-','_')
                date_format = "%Y_%m_%d"
                file_date = datetime.strptime(temp2.split(' ')[0], date_format)
                # Build Year/Month folder structure
                if date_obj != None and creation_date > date_obj and file_date.date() >= date_obj.date():

                    year_folder = date_obj.strftime("%Y")
                    month_folder = date_obj.strftime("%m")
                    day_folder = date_obj.strftime("%d")
                    new_path = os.path.join(year_folder, year_folder + "_" + month_folder,
                                            year_folder + "_" + month_folder + "_" + day_folder)
                 #   print(f"Date taken: {new_path}")

                else:
                    if src_path.split('\\')[0] > '2000' and src_path.split('\\')[0] < '3000' :
                        if src_path.split('\\')[0] < year_folder:
                            templist = src_path.split('\\')
                            temp = '\\'.join(templist[0:2])
                            tempday = templist[2].split(' ')[0]
                            new_path = os.path.join(temp, tempday.repalace('-', '_'))
                  #          print(f"Date src date [0] file year folder: {new_path}")
                        else:
                            new_path = os.path.join(w_year_folder, w_year_folder + "_" + w_month_folder,
                                                    w_year_folder + "_" + w_month_folder + "_" + w_day_folder)
                   #         print(f"Date src date [0] <= file year folder: {new_path}")
                    elif src_path.split('\\')[1] > '2000' and src_path.split('\\')[1] < '3000':
                        if src_path.split('\\')[1] < w_year_folder:
                            templist = src_path.split('\\')
                            temp = '\\'.join(templist[1:3])
                            tempday = templist[3].split(' ')[0]
                            new_path = os.path.join(temp , tempday.replace('-','_'))
                    #        print(f"Date src date [1] file year folder: {new_path}")
                        else:
                            new_path = os.path.join(w_year_folder, w_year_folder + "_" + w_month_folder,
                                                    w_year_folder + "_" + w_month_folder + "_" + w_day_folder)
                     #       print(f"Date src date [1] <= file year folder: {new_path}")
                    else:
                        new_path = os.path.join(w_year_folder, w_year_folder + "_" + w_month_folder,
                                                w_year_folder + "_" + w_month_folder + "_" + w_day_folder)
                        print(f"Date else {new_path}")


                foldertext = ""
                start = root.find(' ')
                end = len(root)
                if start == -1:  # some folder have context text after date and I want to preserve that
                    foldertext = ''
                else:
                    temp = root[start + 1:end]
                    foldertext = ' ' + temp.lstrip(' -')


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
