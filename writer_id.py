import argparse
from math import log2
import json
import os
import numpy as np

Authors_dict = {}
Author_dict_prob = {}
Authors_dict_prob_lg = {}
Author_prob = {}

FileList = []

parser = argparse.ArgumentParser('parameters')
parser.add_argument('-i', help='-i', action='store_true')
parser.add_argument('-p', help='-p', action='store_true')
parser.add_argument('inputPath', help='input path')
parser.add_argument('jsonPath', help='json path')
args = parser.parse_args()

InputFilePath = args.inputPath + '/'


def p(A):
    print(np.matrix(A))


def copy(x):
    y = [a[:] for a in x]
    return y


def lg_Matrix(matrix):
    logMatrix = [[0 for y in range(26)] for x in range(26)]
    for i in range(26):
        for j in range(26):
            if matrix[i][j] > 0:
                logMatrix[i][j] = log2(matrix[i][j])

    return logMatrix


def ProbabilityMatrix(matrix):
    probabilityMatrix = [[0 for y in range(26)] for x in range(26)]
    for i in range(len(matrix)):
        lineSum = sum(matrix[i])
        for j in range(26):
            probabilityMatrix[i][j] = matrix[i][j] / lineSum
    return probabilityMatrix


def GetTxtFiles():
    FileList.extend(os.listdir('./' + InputFilePath))


def addMatrixes(X, Y):
    result = [[0 for y in range(26)] for x in range(26)]
    for i in range(len(X)):
        for j in range(len(X[0])):
            result[i][j] = X[i][j] + Y[i][j]

    return result


def UpdateAuthorsMatrix(authorName, textMatris):
    if authorName not in Authors_dict:
        Authors_dict[authorName] = textMatris
    if authorName in Authors_dict:
        Authors_dict[authorName] = addMatrixes(Authors_dict[authorName], textMatris)


def ProccessWordsAndAddToMatrix(fileContent):
    tempMatrix = [[0 for y in range(26)] for x in range(26)]

    # print(fileName)
    for word in fileContent.split():
        word = word.lower()
        word = ''.join([i for i in word if not (ord(i) < 97 or ord(i) > 122)])
        charIndex = 0
        while charIndex < (len(word) - 1):
            i = ord(word[charIndex]) - 97
            j = ord(word[charIndex + 1]) - 97
            tempMatrix[i][j] += 1
            charIndex += 1

    # p(tempMatrix)
    return tempMatrix


def AlphabetListToDic(x):
    newDict = dict()
    for i in range(26):
        if x[i] > 0:
            newDict[chr(97 + i)] = x[i]

    return newDict

def AlphabetDicToList(x):
    newList = []
    for i in range(26):
        if chr(97 + i) in x:
            newList.append(x[chr(97 + i)])
        else:
            newList.append(0)

    return newList


def AuthorListToDic(x):
    newDict = dict()
    for i in range(26):
        newDict[chr(97 + i)] = AlphabetListToDic(x[i])
    return newDict

def AuthorDicToList(x):
    newList = []
    for i in range(26):
        newList.append(AlphabetDicToList(x[chr(97 + i)]))

    return newList


def SaveToJSON(data):
    newData = dict()
    for i in data:
        newData[i] = AuthorListToDic(data[i])

    a_file = open(args.jsonPath, "w")
    a_file = json.dump(newData, a_file, indent=4, sort_keys=True)


def LoadFromJSON():
    newDict = dict()
    with open(args.jsonPath, 'r') as fp:
        data = json.load(fp)
    for i in data:
        newDict[i] = AuthorDicToList(data[i])
    return newDict


def train():
    GetTxtFiles()
    x = 0
    while x < len(FileList):
        result = FileList[x].find("___")
        authorsName = FileList[x][0:result]
        file = open(InputFilePath + FileList[x], "r", encoding='UTF-8')
        FileContent = file.read()

        tempMatrix = ProccessWordsAndAddToMatrix(FileContent)
        UpdateAuthorsMatrix(authorsName, tempMatrix)

        if x % 10 == 0:
            print(x)
        x += 1

    SaveToJSON(Authors_dict)


def test():
    spath = list(args.inputPath)
    for letter in range(0, len(spath)):
        if ord(spath[letter]) == 92:
            spath[letter] = ' '

    path = ''.join(spath)

    Authors_dict = LoadFromJSON()
    for author in Authors_dict:
        Author_dict_prob[author] = ProbabilityMatrix(Authors_dict[author])
        Authors_dict_prob_lg[author] = lg_Matrix(Author_dict_prob[author])

    file = open(path, "r", encoding='UTF-8')
    FileContent = file.read()
    testFileMatrix = ProccessWordsAndAddToMatrix(FileContent)
    for Author in\
            Authors_dict_prob_lg:
        prob = 0
        for i in range(26):
            for j in range(26):
                prob += (testFileMatrix[i][j] * Authors_dict_prob_lg[Author][i][j])
            Author_prob[Author] = prob
    i = 0
    for w in sorted(Author_prob, key=Author_prob.get, reverse=True):
        print(w)
        i += 1
        if i>9:
            break


if args.p:
    train()
if args.i:
    test()
