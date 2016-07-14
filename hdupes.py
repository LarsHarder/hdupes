#!/bin/python

# hdupes
#
# finds duplicate files in subdirectories of current directory
#
# Lars Harder
#
# started 20160714

MINSIZEFORFINGERPRINT = 1040        # files smaller than this will not be
                                    # fingerprinted for comparison

import os
import filecmp

# maybe do something better later...
def fingerPrintOfFile(fileName):
    f = open(filename, 'r')
    # read first 16 bytes and 16 bytes starting at 1024
    part1 = f.read(16)
    f.seek(1024)
    part2 = f.read(16)
    return part1 + part2

def compareFileShell(fileName1, fileName2):
    print "SHELLSHELLSHELL"
    result = os.system('cmp  "'+ fileName1 + '" "' + fileName2 + '"')
    #result = os.system('cmp -s '+ fileName1 + ' ' + fileName2)
    print result
    if result == 0:
        return True
    else:
        return False

def compareFile(fileName1, fileName2):
    return filecmp.cmp(fileName1, fileName2, shallow=False)


class HFile:
    nameOfFile = ''
    sizeOfFile = -1
    duplicates = []
    savedFingerprint = ''
    def __init__(self, fileName, fileSize):
        self.nameOfFile = fileName
        self.sizeOfFile = fileSize
        self.duplicates = []


    def fingerprint(self):
        if len(savedFingerprint) > 0:
            return savedFingerprint
        else:
            if self.sizeOfFile > MINSIZEFORFINGERPRINT:
                savedFingerprint = fingerPrintOfFile(self.nameOfFile)
            else:
                savedFingerprint = "no print"
            return savedFingerprint

    def filename(self):
        return self.nameOfFile

    def size(self):
        if self.sizeOfFile == -1:
            self.sizeOfFile = os.path.getsize(self.nameOfFile)
        return self.sizeOfFile

    def __repr__(self):
        return self.nameOfFile + '(' + str(self.sizeOfFile) + ')'

    def addDuplicate(self, aDuplicate):
        self.duplicates.append(aDuplicate)

# used for sorting a list of HFiles
def getFileSize(HFile):
    return HFile.sizeOfFile


def do_the_walk(startPath):
    foundFiles = []
    for (dirpath, dirnames, filenames) in os.walk(os.getcwd()):
        print 'found: ' + str(len(foundFiles)) + "\033[F"
        if dirpath[-1:] != '/':
            dirpath = dirpath + '/'
        for aFile in filenames:
                newFileName = dirpath + aFile
                newFileSize = os.path.getsize(newFileName)
                newFile = HFile(newFileName, newFileSize)
                foundFiles.append(newFile)
    return foundFiles

# create lists of files of the same size and put these lists in a list
# ( group files by size )
def listByFileSize(listOfHFiles):
    listOfLists = []
    startIndex = 0
    endIndex = 0
    while (startIndex < len(listOfHFiles)):
        if endIndex < len(listOfHFiles)-1:
            endIndex = endIndex + 1
        else:
            newList = listOfHFiles[startIndex:]
            listOfLists.append(newList)
            break
        if listOfHFiles[startIndex].size() != listOfHFiles[endIndex].size():
            newList = listOfHFiles[startIndex:(endIndex)]
            listOfLists.append(newList)
            startIndex = endIndex
            endIndex = startIndex - 1 # because it gets incremented at start of loop
    return listOfLists

def findDuplicates(listOfFiles):
    if len(listOfFiles) < 2:
        return []
    duplicates = []
    while len(listOfFiles) > 1:
        candidate = listOfFiles.pop(0)
        dupesToCandidate = []
        for secondFile in listOfFiles:
            if compareFile(candidate.filename(), secondFile.filename()):
                #print "      IDENTICAL"
                candidate.addDuplicate(secondFile)
                dupesToCandidate.append(secondFile)
        for f in dupesToCandidate:
            listOfFiles.remove(f)
        if len(candidate.duplicates) > 0 :
            duplicates.append(candidate)
    return duplicates


def printResults(listOfDuplicates):
    for original in listOfDuplicates:
        print "  +  " + original.filename()
        for duplicate in original.duplicates:
            print "  -  " + duplicate.filename()
        print
        print

def main():
    allFiles = do_the_walk(os.getcwd)
    allFiles = sorted(allFiles, key=getFileSize)
    allFilesGroupedBySize = listByFileSize(allFiles)
    allDuplicates = []
    doneFiles = 0
    print 'f'
    for filesOfASize in allFilesGroupedBySize:
        newDuplicates = findDuplicates(filesOfASize)
        if len(newDuplicates) > 0:
            allDuplicates = allDuplicates + newDuplicates
        doneFiles = doneFiles + len(filesOfASize)
        print 'checked: ' + str(doneFiles) + "\033[F"

    printResults (allDuplicates)
    totalSize = 0
    for f in allFiles:
        totalSize = totalSize + f.size()

    wastedSpace = 0
    for dup in allDuplicates:
        wastedSpace = wastedSpace + dup.size() * len(dup.duplicates)
    print 'Space Wasted: ' + str(wastedSpace) + ' of total size: ' + str(totalSize) + '    ' + str(int(wastedSpace*100/totalSize)) + ' %'


main()
