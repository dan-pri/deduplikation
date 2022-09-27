from pathlib import Path,PurePath
import hashlib
import os
import sys
import time

class FileDat:
    def __init__(self, file_name, file_path, file_size, file_stamp):
        self.file_name = file_name
        self.file_path = file_path
        self.file_size = file_size
        self.file_stamp = file_stamp
    
    def get_name(self):
        return self.file_name
    
    def get_path(self):
        return self.file_path

    def get_size(self):
        return self.file_size

    def get_stamp(self):
        return self.file_stamp

def generate_hash(path):
    print("[CHECK] " + str(path))
    with open(path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest().upper()

def enumerate_data(current_path):
    #Get current Directory content
    dir_content = os.listdir(current_path)

    #Remove not allowed Folders from Directory
    for folder in not_allowed_folders:
        if folder in dir_content:
            dir_content.remove(folder)
    
    #Recursion abort
    if len(dir_content) == 0:
        return
    
    #Enumerate subfolder and files in current folder
    for item in dir_content:
        #if item is subfolder -> Recursion
        if os.path.isdir(current_path / item):
            enumerate_data(current_path / item)

        #if item is File -> get infos an store them in Dictionary
        elif os.path.isfile(current_path / item):
            file = FileDat(item, current_path / item, os.stat(current_path / item).st_size, time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(current_path))))
            hash = generate_hash(current_path / item)
        
            #add Object in Dictionary
            if hash in duplicates:
                duplicates[hash].append(file)
            else:
                duplicates[hash] = [file]
    return

def create_list(start_path):
    start_path = start_path / "duplicates.log"
    with open(start_path, "w") as file:
        file.write("Start: " + time.strftime("%d.%m.%Y %H:%M:%S") + "\n\n")
        for item in duplicates:
            file.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
            file.write("SHA-256: " + item + "\n")
            for data in duplicates[item]:
                file.write("Filename: " + data.get_name() + " | Size: " + str(data.get_size()) + " Bytes | Last modified: " + str(data.get_stamp()) + " Path: " + str(data.get_path()) + "\n")
        print("Durch")

if __name__ == "__main__":
    #File names that are not searched
    not_allowed_folders = [
        "System Volume Information", 
        "$RECYCLE.BIN", 
        "desktop.ini",
        ".DS_Store"
    ]

    #Dictionary for all duplicates
    duplicates = {}

    #Check if argument is given
    if len(sys.argv) != 2:
        print("[ERROR] The programm requires 1 argument")
        sys.exit()

    #Define the path
    start_path = Path(str(sys.argv[1]))

    #Check the path
    if not start_path.exists():
        print("[ERROR] Path not found")
        sys.exit()

    #get duplication
    enumerate_data(start_path)

    #Delete Entrys without duplicates
    del_entry = []
    for item in duplicates:
        if len(duplicates[item]) == 1:
            del_entry.append(item)
    for item in del_entry:
        duplicates.pop(item)

    #create list of duplicate files
    create_list(start_path)
