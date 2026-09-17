"""SortPhotos3 - [copy photos from backup on synology to photos folder correctly sorted].

This module provides [The ability organize photos from a backup copy by year, year_mo, year_mo_day in the destination folder.
this version is specifically setup to handle source from my nas.  it assumes all incoming files start with //].

It handles [specific tasks] and outputs [results/files].

Author: Bill Standke
Date: 09-16-2026
"""
import os
import shutil
import argparse
from datetime import datetime
from PIL import Image

from dateutil.parser import parse
from pathlib import PureWindowsPath, PurePosixPath

def is_windows_path(path_str):
    # Check if it parses as a Windows path with a drive
    p = PureWindowsPath(path_str)
    # Windows paths typically have a drive part (e.g., 'C:\\')
    return len(p.parts) > 1 and p.parts[0].endswith(':')


def is_date(string, fuzzy=False):
    """Return whether the string can be interpreted as a date."""
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False

def get_date_taken(image_path,print_debug):
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
        if print_debug:
            print(f"Error: {e}")
    return None

def organize_by_creation_date(src_folder, dst_folder, ignore_duplicates=True,print_debug=False,lastYearCompleted):
    if not os.path.isdir(src_folder):
        raise FileNotFoundError(f"Source folder does not exist: {src_folder}")

    # Ensure the destination exists
    os.makedirs(dst_folder, exist_ok=True)
    in_cnt = 0
    out_cnt = 0
    save_year = ''
    for root, dirs, files in os.walk(src_folder):
        for filename in files:
            src_path = os.path.join(root, filename)
            tmplist = src_path.split('\\')
            year = tmplist[5]
            if lastYearCompleted != None:
                if year < lastYearCompleted:
                    continue
            convert_filepath_date = False
            in_cnt +=1

            try:
                # Get Windows creation time
                stat_data = os.stat(src_path)
                creation_timestamp = stat_data.st_ctime
                creation_date = (datetime
                                 .fromtimestamp(creation_timestamp))

                date_obj = get_date_taken(src_path,print_debug=False)
                filepath_date = None
                if src_path.startswith('\\\\'):
                    tmplist = src_path.split('\\')
                    year = tmplist[5]
                    if is_date(tmplist[6]):
                        date = tmplist[6]
                        rawfoldername = tmplist[6]
                    elif is_date(tmplist[7]):
                        date = tmplist[7]
                        rawfoldername = tmplist[7]
                    elif is_date(tmplist[7].replace('_','-')):
                       date = tmplist[7]
                       rawfoldername = tmplist[7]
                    elif is_date(tmplist[7].split(' ')[0].replace('_','-')):
                       date = tmplist[7].split(' ')[0]
                       rawfoldername = tmplist[7]
                    elif is_date(tmplist[6].split(' ')[0].replace('_','-')):
                       date = tmplist[6].split(' ')[0]
                       rawfoldername = tmplist[6]
                    else:
                       print(f"error parsing filepath_date {src_path}")
                elif is_windows_path(src_path):
                    if src_path[3] == '\\': #todo
                        #c:\\
                        pass
                    elif src_path[3] == '/':
                        #c:/
                        pass
                else:
                    pass

                try:
                    filepath_date = datetime.strptime(date,'%Y-%m-%d')
                except:
                    filepath_date = datetime.strptime(date, '%Y_%m_%d')

                if date_obj != None :
                    year_folder = date_obj.strftime("%Y")
                    month_folder = date_obj.strftime("%m")
                    day_folder = date_obj.strftime("%d")
                    new_path = os.path.join(year_folder, year_folder + "_" + month_folder,
                                            year_folder + "_" + month_folder + "_" + day_folder)
                    if print_debug:
                        print(f"Date taken: {date_obj}")
                elif creation_date <= filepath_date:
                    year_folder = creation_date.strftime("%Y")
                    month_folder = creation_date.strftime("%m")
                    day_folder = creation_date.strftime("%d")
                    new_path = os.path.join(year_folder, year_folder + "_" + month_folder,
                                            year_folder + "_" + month_folder + "_" + day_folder)
                    if print_debug:
                                print(f"creation_date: {creation_date}")
                else:
                    year_folder = filepath_date.strftime("%Y")
                    month_folder = filepath_date.strftime("%m")
                    day_folder = filepath_date.strftime("%d")

                    new_path = os.path.join(year_folder, year_folder + "_" + month_folder,
                                                    year_folder + "_" + month_folder + "_" + day_folder)
                    if print_debug:
                                print(f"Filepath_date: {filepath_date}")

                if print_debug:
                    print(f"New Path: {new_path}")
                foldertext = ""
                start = rawfoldername.find(' ')
                end = len(rawfoldername)
                if start == -1:  # some folder have context text after date and I want to preserve that
                    foldertext = ''
                else:
                    temp = rawfoldername[start + 1:end]
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
                out_cnt += 1
                #original_stat = os.stat(src_path)
                #os.utime(dst_path, (original_stat.st_atime, original_stat.st_mtime))
                if print_debug:
                    print(f"Copied: {src_path} → {dst_path}")

            except Exception as e:
                print(f"Error processing {src_path}: {e}")

            if year != save_year:
               print(f"{save_year} IN: {in_cnt-1} Out: {out_cnt-1}")
               save_year = year
               in_cnt = 1
               out_cnt = 1


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
        default=False,
        help="printed Debug."
    )
    parser.add_argument(
        "-i", "--ignore-duplicates",
        action="store_true",
        help="Skip files that already exist in the target folder."
    )

    parser.add_argument(
        "-l", "--last-year-completed",
        action="store_true",
        help="folder of last year completed."
    )

    parser.add_argument(
        "-y", "--list-year-ndx",
        action="store_true",
        help="index position of year when file path is split into list."
        #for example in this example \\infinity\backups\photos\2018\2018_06_28 Glacier Jeffs and Dans\IMG_2153.MOV  the index is position 5
    )


    args = parser.parse_args()

    organize_by_creation_date(
        src_folder=args.source,
        dst_folder=args.destination,
        ignore_duplicates=args.ignore_duplicates,
        print_debug = args.print_debug,
        lastYearCompleted= args.last-year-completed
    )


if __name__ == "__main__":
    main()
