# -*- coding: utf-8 -*-

import functions, sys
from Tkinter import *
from tkFileDialog import askopenfiles

args = functions.includeParser() #запускаем парсер аргументов и сохраняем их.

if args.silent == False: #Выбираем тихий или громкий режим
    functions.debugOutput(u"Включен оконный режим, WIP.")
    functions.drawWindow()
else: #весь тихий режим тут, вплоть до выхода
    if (args.input != None) & (args.mopedit != None):
        print u"Работа возможна только или с переводом из аут в моп или обработкой .mop"
        exit()
    if (args.input != None):
        functions.debugOutput(u"Включен безоконный режим.")
        try:
            inputFile = open(args.input, mode = "r")
        except IOError:
            print "Файл не найден. Опечатка в названии?"
            exit()
        except TypeError:
            print "Похоже, вы забыли аргумент -a."
            exit()
        functions.debugOutput(u"Файл открыт успешно.")
        if functions.checkForDONE(inputFile) != True:
            inputFile.close()
            exit()

        if args.mop != None:
            newMopFile = open(args.mop, "w")
            functions.mopGenerate(False, inputFile, newMopFile)
            newMopFile.close()

        if args.old != None:
            newMopFile = open(args.old, "w")
            functions.mopGenerate(True, inputFile, newMopFile)
            newMopFile.close()

        functions.debugOutput(u"Тихий режим отработал. Закрываемся.")
        exit() 
    if (args.mopedit != None):
        if args.fix == None & args.fixall == None & args.unfixall == None:
            print u"Не указанно задание."
            exit()

        exit()