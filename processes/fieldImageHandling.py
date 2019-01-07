#!/usr/bin/env python
import glob
import os
import shutil
import piexif    #Manipulate exif data, this lets us keep the field number associated with the catalog number

# Portals expect the image to be named according to the catalog number.
# We (optionally) assign catalog numbers after identification has taken place in the lab.
# this module converts the field-number-named jpgs generated on mobile into catalog-number-named jpgs
# this module also has functions to submit the catalog-nuber-named jpgs directly into the database.

# Contains 2 non-standard libraries, the iRODS is probably unavoidable.
# Piexif may be replaceable, I'm not sure.

#note, mobile app is organizing images as such:
# .jpg file, stored by date of collection
# sites listed as "site##.jpg" where ## is the site number (in the field number)
# specimens listed as "specimen##-##.jpg" where ##-## is the entire field number.
# all circumstances, the number of digits should be considered non-discrete.

#TODO

# All upload functions need to return confirmation of successful transmission
#   It may be easiest to wrap the save functions into a function to check for return confirmation and pass or retry the batch
# Upon successful uploads, the outgoing files should be cleaned up from the folder.
#   This implies a single outgoing folder to fill and then empty each transmission. To simplify the outgoing flow.
#   Not necessarily removing the files from the user's storage directory... we'll have to find a nice way to figure out if the user caresa bout them anymore
# Need to describe site photos as identifying habitat.
#   What happens when Symbiota portal image upload form has the "is habitat" checkbox selected?
#   Because we need to emulate that!


def renameImageFile(key, oldFileName, newFileName, outputFolder, payloadFolder = None):
    """ Accepts an image path and copies while renaming it
    key = the key from the recordDict, which should correspond to the field number. Passing this to avoid addtl. work.
    oldFileName = the field-number-named file which needs to be renamed and moved
    newFileNAme = the desired new name after moving
    outputFolder = the folder to save the catalog-number-named file
    payloadFolder = the folder to congregate to be transfered files, if not passed presumes it is the same as outputFolder
    """
    if payloadFolder == None:
        payloadFolder = outputFolder
        
    newFileNames = []   #start with an empty list....
    for destFolder in set([outputFolder, payloadFolder]):
        newFileNames.append(str(destFolder + '/{}.jpg'.format(newFileName)))    #Build a list of paths to copy the orig file to.

# see this example for concerns about loss of metadata upon image copy:
#   https://stackoverflow.com/questions/6106303/how-to-rename-a-file-and-preserve-creation-date-in-python

    stat = os.stat(oldFileName)  #Take note of creation and modification metadata from initial file    
    for outputName in newFileNames:             # for each filepath we're copying to
        os.makedirs(os.path.dirname(outputName), exist_ok=True)
        shutil.copy2(oldFileName, outputName)   # copy the origional and rename it according to the outputName

# insert metadata
        metaDataDict = {'otherCatalogNumber':key}  #This dict can be altered to add ... everything?
        zeroth_ifd = {270: str(metaDataDict)}    #converting dict to string to embed it into the same field
        exif_bytes = piexif.dump({"0th":zeroth_ifd})
        os.utime(outputName, (stat.st_atime, stat.st_mtime))   #Write orig creation and modification metadata to the copied file

#debugging creation time metadata loss
#        print(stat)
#        print(os.stat(outputName))
        piexif.insert(exif_bytes,outputName)
        
        #we should consider adding an option to insert the ENTIRE record to the metadata.
        # But for now, this is nice insurance against de-linking the field notes from the specimen image.

def convertImageFiles(recordDict, incomingFolder, outputFolder, payloadFolder):
    """ Expects a dictionary of field numbers and catalog numbers. Uses this dictionary to copy the field photos with catalog names ready for submission.
    Places the now-properly-named folders into a payload folder to be passed to the appropriate image uploader as the "local path"
    recordDict = dictionary built as fieldNumber:catalogNumber, does not need to be handed site only records (this is how we'll filter site photos without specimen records)
    incomingFolder = directory where the origional, input, field-number-named images rest
    outputFolder = directory where the copied, output, catalog-number-named images will be placed
    payloadFolder = hopefully temporary location for the to be transmitted files to congregate
    """
    inputImgList = glob.glob(str(incomingFolder + '/*.jpg')) #build a list of every .jpg file in the folder we were told to expect field Images

#example recordDict =  {21-17:UCHT-F-000010, 21-18:UCHT-F-000011, 22-19:UCHT-F-000012}
  #   stat = os.stat(myfile)
  #  // your code - rename access and modify your file
  #  os.utime(my_new_file, (stat.st_atime, stat.st_mtime))
                             
    for key in recordDict.keys():       #we expect the keys to be a list of field numbers
        newFileNameBase = recordDict.get(key)
        fieldRecordImages = glob.glob(str(incomingFolder + '/*specimen{}*.jpg'.format(key)))

        for count, oldFileName in enumerate(fieldRecordImages, 1):
            print(oldFileName)
            if count == 1:
                newFileName = str(newFileNameBase)
                renameImageFile(key, oldFileName, newFileName, outputFolder, payloadFolder)
            else:
                newFileName = str(newFileNameBase + c)
                renameImageFile(key, oldFileName, newFileName, outputFolder, payloadFolder)
                             


def iRODSUploadImages(host, port, username, password, zone, remotePath, localPath):
    """ Uploads an entire folder to provided iRods folder. If the folder is non-existant it attempts to create it first.
    host = .org, .com, .edu site address for the iRods content
    port = iRods transfer port
    username = your user name
    password = user password
    zone = iRods zone (some sort of folder classification system? get zome info from workflow
    remotePath = The absolute path in your iRODS Folders to save the images (can pass non-existant paths to attempt to create them)
    localPath = the folder you want to upload, it is the ENTIRE folder that will go.

    #Requires non-standard module
        #https://github.com/irods/python-irodsclient/
    #Modified from this example code:
        #https://github.com/cyverse/Robotframework-iRODS-Library/blob/master/src/iRODSLibrary/iRODSLibrary.py
        #^I think this person is logging robot data on irods!
    """
    from irods.session import iRODSSession
    from irods.models import Collection, DataObject

    with iRODSSession(self, host=host, port=port, user=username, password=password,zone=zone) as session:   #"Log in" basically..
        pass

    imgList = glob.glob(str(localPath + '/*.jpg')

    for fieldImage in imgList:
        #session = self._cache.switch(alias)    #not entirely sure of this purpose, but I believe it's taken care of with iRODSSession at head of this func.
        try:
            data_obj = session.data_objects.create(remotePath)
        except:                                                         #no actual accept errors? Are we catching everything here?
            data_obj = session.data_objects.get(remotePath)        #looks like a "file already exists" senerio we're planning for?
        finally:
            file_local = open(fieldImage, 'rb')
            payload = file_local.read()
            file_irods = data_obj.open('r+')
            file_irods.write(payload)
            file_local.close()
            file_irods.close()


def ftpUploadImages(server, port, username, password, remotePath, localPath):
    """ Uploads an entire folder to provided ftp folder. If the folder is non-existant it attempts to create it first.
    server = ftp server address
    port = ftp server's port number
    username = your user name
    password = user password
    remotePath = The absolute path in your ftp Folders to save the images (can pass non-existant paths to attempt to create them)
    localPath = the folder you want to upload, it is the ENTIRE folder that will go.

    #Requires standard ftp module
        #https://docs.python.org/3/library/ftplib.html
    """
    import ftplib

    ftp_connection = ftplib.FTP(server, username, password) #establish connection parameters

# See this old answer, but was followed here for path check / generate:
# https://stackoverflow.com/questions/10644608/create-missing-directories-in-ftplib-storbinary

     if directory_exists(remotePath) is False: # (or negate, whatever you prefer for readability)
        ftp_connection.mkd(remotePath)  #these may need to be ftp.mkd and ftp.cwd
        ftp_connection.cwd(remotePath)
    else:
        ftp_connection.cwd(remotePath) #set working directory to the Destination location for the files

    imgList = glob.glob(str(localPath + '/*.jpg')

    for fieldImage in imgList:
        fh = open(fieldImage, 'rb')
        ftp_connection.storbinary(str('STOR ' + fieldImage), fh)
        fh.close()  #close out the file we opened to read then write
        ftp.quit()  #close out ftp connection, no reason to leave this to hang.
