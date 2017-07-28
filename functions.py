# -*- coding: cp1251 -*-

import argparse, re
from tkFileDialog import asksaveasfile, askopenfiles, askopenfile
from Tkinter import *

global args
global checkedBoxes
global inputFiles
global openTextbox
global regexpForFix
checkedBoxes = {}


def includeParser():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help = "Verbose mode. More technical output.", action = "store_true")
    parser.add_argument("-s", "--silent", help = "Windowless mode. You have to use at least -a argument.", action = "store_true")
    parser.add_argument("-i", "--input", help = "Path to .out file", type = str)
    parser.add_argument("-m", "--mop", help = "Create new .mop file. Use -m 'path/to/file'", type = str)
    parser.add_argument("-o", "--old", help = "Create old .mop file. Use -o 'path/to/file'", type = str)

    parser.add_argument("-me", "--mopedit", help = "File to fix/unfix", type = str)
    parser.add_argument("-f", "--fix", help = "Pattern {} ^{}", type = str)
    parser.add_argument("--fixall", help = "Fix all atoms {*}:{}", action = "store_true")
    parser.add_argument("--unfixall", help = "Unfix all atoms {}:{*}", action = "store_true")

    args = parser.parse_args()
    debugOutput(u"��������� �� ����� " + str(args))
    return args

def findStrInFile(string, file, start = 0):    #���������� ��������� �� ������ ������. ���� �� ���������� ������ ������.
    positionOnStart = file.tell() #���������� ��� ��� ������ ����
    file.seek(start) #�������� ����� � ������
    strLenght = len(string)
    position = -1
    while True:
        strInFile = file.readline()
        #print strInFile
        if strInFile == "":
            break
        if strInFile.strip()[0:strLenght] == string: #����� �������� ���������� ������� � ������ � �����
            position = file.tell() - len(strInFile)
            break
    file.seek(positionOnStart) #���������� �� �����
    return position

def debugOutput(string):
    if args.verbose:
        print string
    return

def checkForDONE(file):
    if findStrInFile("== MOPAC DONE ==", file) == -1:
        print u"���-�� � ������ �� ���. �� ������� ������ == MOPAC DONE =="
        return False
    debugOutput(u"== MOPAC DONE == ������, ��������� ������.")
    return True

def mopStringFix(strings): #���� ����� ������� �� �������, ��� ������ �� ������ 999
    outStr = []
    #print strings
    for string in strings:
        if string[36] == "*":
            tmp = string[0:36] + "1" + string[37:]
        if string[36] == " ":
            tmp = string[:36] + "0" + string[37:]
        if string[52] == "*":
            tmp = tmp[0:52] + "1" + tmp[53:]
        if string[52] == " ":
            tmp = tmp[:52] + "0" + tmp[53:]
        if string[68] == "*":
            tmp = tmp[0:68] + "1" + tmp[69:]
        if string[68] == " ":
            tmp = tmp[:68] + "0" + tmp[69:]
        tmp = tmp[8:]
        tmp = tmp.strip() + "\n"
        outStr.append(tmp)
    return outStr

def mopGenerate(old = False, inputFile = file, newFile = file):
    
    if old:
        posForMop = findStrInFile("ATOM    CHEMICAL", inputFile)  #����� ������ ������ �������� �� ATOM    CHEMICAL
        lenPosition = findStrInFile("Empirical Formula", inputFile)    #����� � �� ����� �� Empirical Formula: C20 H42 O11  =    73 atoms
        argsForMop = findStrInFile("-------------------------------------------------------------------------------", inputFile)    #����� ������ ���������� ������������� �����
    else:
        posForMop = findStrInFile("COMPUTATION TIME", inputFile)  #����� ������ ���������������� �������� �� COMPUTATION TIME
        lenPosition = findStrInFile("Empirical Formula", inputFile)    #����� � �� ����� �� Empirical Formula: C20 H42 O11  =    73 atoms
        argsForMop = findStrInFile("-------------------------------------------------------------------------------", inputFile)    #����� ������ ���������� ������������� �����
    
    inputFile.seek(posForMop)

    if old:
        for i in range(3):
            inputFile.readline()
    else:
        for i in range(8):
            inputFile.readline()

    posForMop = inputFile.tell() #������ ����, ��� ���� � .mop


    #���� �����.
    inputFile.seek(lenPosition)
    inputFile.readline()
    inputFile.seek(-14 ,1)
    mopLenght = int(inputFile.readline()[:-6].strip())

    inputFile.seek(posForMop)
    linesToMop = inputFile.readlines()[:mopLenght]

    inputFile.seek(argsForMop)
    inputFile.readline() #���������� ��� ������
    arguments = inputFile.readline()

    linesToMopFixed = mopStringFix(linesToMop)

    #��������� ��� ����� �� ������ ��������
    filePath = newFile.name.encode('utf-8') #����� ������������� ��������
    for i in range(len(filePath)):
        if (filePath[-i] == "/") or (filePath[-i] == "\\"): #��� \ �������������
            nameLen = i - 1
            break
        else:
            nameLen = len(filePath)

    fileName = filePath[-nameLen:]

    #���������������� �������� �������� � ���������� ���
    #� ����� ���� �������: ������ ����������, �������� �����, ������ ������, ���������� ��������(, ��� ������ ������?).
    newFile.writelines(arguments)
    newFile.writelines(fileName) 
    newFile.writelines("\n\n")
    newFile.writelines(linesToMopFixed)

    if old:
        debugOutput(u"������ .mop ���� ������������")
    else:
        debugOutput(u"���������������� .mop ���� ������������")
    return True

def infoBarWrite(string):
    infoLabel["text"] = string
    return

def writeReport():
    reportFile = asksaveasfile()
    reportFile.write("�������������        �������     �������\n")
    for i in range(len(normalFiles)):
        file = normalFiles[i]
        reportFile.write(u"..." + file.name[-17:] + " " + energyArray[i] + " " + heatArray[i] + "\n")

    reportFile.close()
    infoBarWrite(u"����� ��������.")
    return

def writeFiles():
    if checkedBoxes["opt"].get():
        for file in normalFiles:
            newMopFile = open(file.name[:-4] + ".opt.mop", mode = "w")
            mopGenerate(False, file, newMopFile)
            newMopFile.close()
    if checkedBoxes["old"].get():
        for file in normalFiles:
            newMopFile = open(file.name[:-4] + ".old.mop", mode = "w")
            mopGenerate(True, file, newMopFile)
            newMopFile.close()
    infoBarWrite(u"����� �������������.")
    return

def workWithFiles(fileList):
    global energyArray, heatArray
    energyArray = []
    heatArray = []
    for i in range(len(fileList)):
        file = fileList[i]
        openTextbox.insert(str(i+1) + ".0", u"�" + file.name[-19:])

        totEnergyPos = findStrInFile("TOTAL ENERGY", file)
        file.seek(totEnergyPos + 36)
        totEnergyStr = file.readline().strip()
        totalEnergyColumn.insert(str(i) + ".0", totEnergyStr[:-3] + '\n')
        energyArray.append(totEnergyStr[:-3])

        heatPos = findStrInFile("FINAL HEAT", file)
        file.seek(heatPos + 64)
        theatStr = file.readline().strip()
        finalHeatColumn.insert(str(i) + ".0", theatStr[:-7] + '\n')
        heatArray.append(theatStr[:-7])

    infoBarWrite(u"����� ����������")
    return

def clearTextboxes():
    openTextbox.delete('1.0', END)
    totalEnergyColumn.delete('1.0', END)
    finalHeatColumn.delete('1.0', END)
    return

def openOutFiles(): #����� �� ������ �����������, �� ��� � �����������
    global normalFiles
    try:
        for file in inputFiles: #��� ������������ ������� ��� ����� �������� �����
            file.close()
    except UnboundLocalError:
        pass

    inputFiles = askopenfiles(filetypes = [(u"�������� ���� ������", ".out")])
    clearTextboxes()
    normalFiles = []
    for file in inputFiles:
        if checkForDONE(file):
            normalFiles.append(file)

    if len(inputFiles) == len(normalFiles):
        isOKlabel["text"] = u"��� ����� ���������"
        isOKlabel["fg"] = "green"
    if len(inputFiles) != len(normalFiles):
        isOKlabel["text"] = u"���� ������������ �����"
        isOKlabel["fg"] = "yellow"
    if len(normalFiles) == 0:
        isOKlabel["text"] = u"�� ���� ���� �� ��������"
        isOKlabel["fg"] = "red"

    normalFiles
    
    workWithFiles(normalFiles)

    #�������� ������
    writeFilesButton["state"] = NORMAL
    toFileButton["state"] = NORMAL

    return

def mopOpen():
    global mopFile
    mopFile = askopenfile(filetypes = [(u"������� ���� ������", ".mop")], mode = "r")
    mopEditWindow.tkraise()
    if mopFile == None:
        return
    mopEntry["state"] = NORMAL
    mopWriteButton["state"] = NORMAL
    mopFixallButton["state"] = NORMAL
    mopUnfixallButton["state"] = NORMAL
    if mopEntry.get() == "":
        #mopEntry.insert(0, "{}:{}")
        mopEntry.insert(0, "{1,2,4-6,8}:{*}")
    mopLenghtLabel["text"] =  u"������: " + str(len(mopFile.readlines()) - 3) #8 �������� � u"������: "
    return

def lineEdit(line, number): #���������� �� ���������
    global regexpForFix
    regexpReplace = r"\g<1>" + str(number) + r"\g<2>" + str(number) + r"\g<3>" + str(number) + r"\g<4>"
    line = regexpForFix.sub(regexpReplace, line)
    #print line
    return line

def mopFixer():
    global mopFile
    #��������� ������ ��������� �� ������������
    string = mopEntry.get().strip()
    if re.match("^\{[0-9 ,-/*]*\}:\{[0-9 ,-/*]*\}$", string) == None:
        print u"��������� ����������� � �������, ���������� ��� ���."
        return
    onesAndZeros = string.split(":")
    onesAndZeros[0] = onesAndZeros[0][1:-1]
    onesAndZeros[1] = onesAndZeros[1][1:-1]
    #print onesAndZeros
    finalArray = ["������� �������"]
    #print len(finalArray)
    whereStar = ""
    for symbol in onesAndZeros[0]:
        if symbol == "*":
            whereStar = "0"
    for symbol in onesAndZeros[1]:
        if symbol == "*":
            whereStar = "1"
    for i in range(int(mopLenghtLabel["text"][8:])):
        finalArray.append(whereStar)
    
    stringOfZeros = []
    stringOfOnes = []

    for i in onesAndZeros[0].split(","):
        if i == "*":
            stringOfZeros = []
            break

        try:
            int(i)
            stringOfZeros.append(int(i))
        except ValueError:
            i = i.split("-")
            print i
            try:
                for j in range(int(i[0]), int(i[1])+1):
                    stringOfZeros.append(j)
            except ValueError:
                pass
    for i in onesAndZeros[1].split(","):
        if i == "*":
            stringOfOnes = []
            break
        try:
            int(i)
            stringOfOnes.append(int(i))
        except ValueError:
            i = i.split("-")
            print i
            try:
                for j in range(int(i[0]), int(i[1])+1):
                    stringOfOnes.append(j)
            except ValueError:
                pass
    stringOfZeros = sorted(stringOfZeros)
    stringOfOnes = sorted(stringOfOnes)
    #print stringOfZeros
    #print stringOfOnes

    try:
        for i in stringOfZeros:
            finalArray[i] = "0"
        for i in stringOfOnes:
            finalArray[i] = "1"
    except IndexError:
        print u"������� �������� �������������� ����."
        return

    print finalArray[1:]

    """
    #��������� ������ � ������
    #������������ ������ ������
    #�������: ������ ���� "0"
    #���� � ����� ����� *, ��� ������ ������
    #���� � �����, �� ������ ������������ "0"
    #�������: ������, � ������� ���������� ������ �����, ��� ����� "1". ��������� ���.
    #���������� ������ ������ �����.
    #�������� ������� �������, ����� ����.
    #������� ������������� ������ ["1", "0", "1", "0", "", "1", "0"], ������� ������� ������, ����� ���������
    #���� ���� ���������, �� ��� ������������� ���������� ������� �������� ��� ����� "�������" ���������� (1)
    #��� ������ ������ - �� ��������
    """
    
    mopFileName = mopFile.name
    mopFile.close()
    mopFile = open(mopFileName, "r")
    mopLines = mopFile.readlines()
    mopFile.close()
    mopFile = open(mopFileName, "w")
    #print mopLines[:3]

    for i in range(len(finalArray)):
        if finalArray[i] == "1":
            mopLines[i+2] = lineEdit(mopLines[i+2], 1)
        if finalArray[i] == "0":
            mopLines[i+2] = lineEdit(mopLines[i+2], 0)
    #print mopLines
    for line in mopLines:
        mopFile.writelines(line)
    #��������� ��� ����� readlines, ��������� ���� �� ������, ��������� �� ����������
    #������������ ��������� ������
    #���������� �� � ����
    #��������� ����
    mopFile.close()
    return

def mopFixall():
    mopEntry.delete(0, END)
    mopEntry.insert(0, "{*}:{}")
    return

def mopUnfixall():
    mopEntry.delete(0, END)
    mopEntry.insert(0, "{}:{*}")
    return

def mopEditor():
    global mopEditWindow, mopWriteButton, mopLenghtLabel, mopFixallButton, mopUnfixallButton, mopEntry, regexpForFix
    regexpForFix = re.compile(r"^([\s]*[\w][\s]+[0-9.-]{8,}[\s]+)[0-1]([\s]+[0-9.-]{8,}[\s]+)[0-1]([\s]+[0-9.-]{8,}[\s]+)[0-1](.*)$")
    #������� ������ ��� ��� �� ���� ��� ����������

    mopEditWindow = Toplevel()
    mopEditWindow.resizable(False, False)
    mopEditWindow.title("MopEdit")

    mopOpenButton = Button(mopEditWindow, text = u"����� �����", command = mopOpen)
    mopWriteButton = Button(mopEditWindow, text = u"�������� � ����", command = mopFixer, state = DISABLED)
    mopLenghtLabel = Label(mopEditWindow, text = u"���������� ������")
    mopFixallButton = Button(mopEditWindow, text = u"FixAll", command = mopFixall, state = DISABLED)
    mopUnfixallButton = Button(mopEditWindow, text = u"UnfixAll", command = mopUnfixall, state = DISABLED)
    mopEntry = Entry(mopEditWindow, width = 30, state = DISABLED)

    mopOpenButton.grid(column = 0, row = 0, columnspan = 2)
    mopLenghtLabel.grid(column = 0, row = 1, columnspan = 2)
    mopEntry.grid(column = 0, row = 2, columnspan = 2)
    mopFixallButton.grid(column = 0, row = 3, sticky = "e")
    mopUnfixallButton.grid(column = 1, row = 3, sticky = "w")
    mopWriteButton.grid(column = 0, row = 4, columnspan = 2)
    return

def drawWindow():
    global checkedBoxes, openTextbox, isOKlabel, totalEnergyColumn, finalHeatColumn, infoLabel, writeFilesButton, toFileButton

    root = Tk()
    root.resizable(False, False)
    root.title("MopPy")

    checkedBoxes["old"] = BooleanVar()
    checkedBoxes["opt"] = BooleanVar()

    infoLabel  = Label(root, text = u"�������.", bg = "gray", width = 85)
    mainFrame = Frame(root)

    openFrame = Frame(mainFrame, bd = 5)
    reportFrame = Frame(mainFrame, bd = 5)
    checkboxFrame =  Frame(mainFrame, bd = 5)

    openButton = Button(openFrame, text = u"������� �����", command = openOutFiles)
    openTextbox = Text(openFrame, height = 7, width = 20)
    isOKlabel = Label(openFrame, text = u"��� � �������?", fg = "black")

    toFileButton = Button(reportFrame, text = u"�������� ����� � ����", command = writeReport, state = DISABLED)
    linesFrame = Frame(reportFrame)

    #��������
    totalEnergyLabel = Label(linesFrame, text = u"Total Energy EV")
    totalEnergyColumn = Text(linesFrame, height = 7, width = 15)

    finalHeatLabel = Label(linesFrame, text = u"Final Heat kJ/mol")
    finalHeatColumn = Text(linesFrame, height = 7, width = 15)
    #/��������

    checkboxesFrame = Frame(checkboxFrame)
    writeFilesButton = Button(checkboxFrame, text = u"������� �����", command = writeFiles, state = DISABLED)

    #��������
    oldMopCheck = Checkbutton(checkboxesFrame, text = u"������ .mop", variable = checkedBoxes["old"], onvalue = True, offvalue = False)
    optMopCheck = Checkbutton(checkboxesFrame, text = u"���������������� .mop", variable = checkedBoxes["opt"], onvalue = True, offvalue = False)
    #/��������
    openMopEditor = Button(checkboxFrame, text = u"�������� .mop", command = mopEditor) #���� ������� � checkboxFrame


    infoLabel.pack(side = "bottom") #�������� ����
    mainFrame.pack(side = "bottom")

    openFrame.pack(side = "left")       #����� ��� �������� ������
    reportFrame.pack(side = "left")     #����� � ������� �����
    checkboxFrame.pack(side = "bottom") #����� � ����������

    openButton.pack(side = "bottom")    #����� ��� �������� ������
    openTextbox.pack(side = "bottom")
    isOKlabel.pack(side = "bottom")

    toFileButton.pack(side = "bottom")  #����� � ������� �����
    linesFrame.pack(side = "bottom")

    totalEnergyLabel.grid(row = 0, column = 0)
    totalEnergyColumn.grid(row = 1, column = 0)
    finalHeatLabel.grid(row = 0, column = 1)
    finalHeatColumn.grid(row = 1, column = 1)

    checkboxesFrame.pack(side = "top")  #����� � ����������
    writeFilesButton.pack(side = "top")
    openMopEditor.pack(side = "bottom")
    oldMopCheck.pack(side = "top", anchor = "w")
    optMopCheck.pack(side = "top", anchor = "w")

    root = mainloop()

    return