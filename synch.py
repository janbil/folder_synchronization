import os
import shutil
import sys
import hashlib
import time
import argparse

#Checks whether two files are identical. Uses md5 
def isSameFile(file1, file2):
    with open(file1, 'rb') as f1:
        with open(file2, 'rb') as f2:
            if hashlib.md5(f1.read()).hexdigest() == hashlib.md5(f2.read()).hexdigest():
                return True
            else:
                return False

#Log of change of file     
def log_change(log_file, path):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    str = now + "  " +"File changed: " + path
    with open(log_file, 'a') as f:
        f.write(str+ "\n")
    print(str)

#Log of creation of file   
def log_create(log_file, path):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    str = now + "  " +"File created: " + path
    with open(log_file, 'a') as f:
        f.write(str + "\n")
    print(str)

#Log of deletion of file   
def log_delete(log_file, path):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    str = now + "  " +"File deleted: " + path
    with open(log_file, 'a') as f:
        f.write(str+ "\n")
    print(str)

#Log of deletion of directory   
def log_delete_dir(log_file, path):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    str = now + "  " +"Directory deleted: " + path
    with open(log_file, 'a') as f:
        f.write(str+ "\n")
    print(str)

#Log of creation of directory  
def log_create_dir(log_file, path):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    str = now + "  " +"Directory created: " + path
    with open(log_file, 'a') as f:
        f.write(str+ "\n")
    print(str)

#Function handeling creations and changes
def handle_directory(dir_name, replica_dir_name, log_file):
    #Loop through all entries in source directory
    entries = os.listdir(dir_name)
    for entry in entries:
        replica_path = os.path.join(replica_dir_name, entry)
        path = os.path.join(dir_name, entry)
        if os.path.isfile(path):
            #If file present in both folders
            if os.path.isfile(replica_path):
                #If is not identical, log change and copy from source
                if not isSameFile(path, replica_path):
                    log_change(log_file, replica_path)
                    os.system('cp '+path+' '+replica_path)
            #If is not present in replica, copy it and log creation
            else:
                log_create(log_file, replica_path)
                os.system('cp '+path+' '+replica_path)
        #If is directory
        else:
            #If not present in replica, create folder and log
            if not os.path.isdir(replica_path):
                log_create_dir(log_file, replica_path)
                os.mkdir(replica_path)
            #Recursively loop through this directory
            handle_directory(path, replica_path, log_file)

#Function handling deletions
def delete_unwanted(dir_name, replica_dir_name, log_file):
    #Loop through all entries in replica directory
    entries = os.listdir(replica_dir_name)
    for entry in entries:
        replica_path = os.path.join(replica_dir_name, entry)
        path = os.path.join(dir_name, entry)
        #If file in relica and not in source, delete it and log
        if os.path.isfile(replica_path):
            if not os.path.isfile(path):
                log_delete(log_file, replica_path)
                os.remove(replica_path)
        
        else:
            #If directory in replica and not in source, delete it and log
            if not os.path.isdir(path):
                log_delete_dir(log_file, replica_path)
                shutil.rmtree(replica_path, ignore_errors=False, onerror=None)
            #Else recursively loop folder
            else:
                delete_unwanted(path, replica_path, log_file)

#Setup argument parser
parser = argparse.ArgumentParser(description='Synchronizes 2 files periodicaly and logs changes')
#Set arguments
parser.add_argument('-s', '--source_folder', required=True, help='Path of the source folder')
parser.add_argument('-r', '--replica_folder', required=True, help='Path of the replica folder')
parser.add_argument('-i', '--interval', type=int, default=10, help= 'Time interval between synchronizations in seconds, default = 10')
parser.add_argument('-l', '--log_file', default='log_file.txt', help= 'Path to a log file, default is log_file.txt')
args = parser.parse_args()
#Infinite loop
while(True):
    #Source folder should exist
    if(not os.path.isdir(args.source_folder)):
        raise Exception("Source folder path is not a directory!")
    #Create relica folder if necessery
    if(not os.path.isdir(args.replica_folder)):
        os.mkdir(args.replica_folder)
        log_create_dir(args.log_file, args.replica_folder)
    #Call synchronization functions
    handle_directory(args.source_folder, args.replica_folder, args.log_file)
    delete_unwanted(args.source_folder, args.replica_folder, args.log_file)
    #Sleep for given interval
    time.sleep(args.interval)