import codecs
import os

buck2uni = {"'": u"\u0621",  # hamza-on-the-line
            "|": u"\u0622",  # madda
            ">": u"\u0623",  # hamza-on-'alif
            "&": u"\u0624",  # hamza-on-waaw
            "<": u"\u0625",  # hamza-under-'alif
            "}": u"\u0626",  # hamza-on-yaa'
            "A": u"\u0627",  # bare 'alif
            "b": u"\u0628",  # baa'
            "p": u"\u0629",  # taa' marbuuTa
            "t": u"\u062A",  # taa'
            "v": u"\u062B",  # thaa'
            "j": u"\u062C",  # jiim
            "H": u"\u062D",  # Haa'
            "x": u"\u062E",  # khaa'
            "d": u"\u062F",  # daal
            "*": u"\u0630",  # dhaal
            "r": u"\u0631",  # raa'
            "z": u"\u0632",  # zaay
            "s": u"\u0633",  # siin
            "$": u"\u0634",  # shiin
            "S": u"\u0635",  # Saad
            "D": u"\u0636",  # Daad
            "T": u"\u0637",  # Taa'
            "Z": u"\u0638",  # Zaa' (DHaa')
            "E": u"\u0639",  # cayn
            "g": u"\u063A",  # ghayn
            "_": u"\u0640",  # taTwiil
            "f": u"\u0641",  # faa'
            "q": u"\u0642",  # qaaf
            "k": u"\u0643",  # kaaf
            "l": u"\u0644",  # laam
            "m": u"\u0645",  # miim
            "n": u"\u0646",  # nuun
            "h": u"\u0647",  # haa'
            "w": u"\u0648",  # waaw
            "Y": u"\u0649",  # 'alif maqSuura
            "y": u"\u064A",  # yaa'
            "F": u"\u064B",  # fatHatayn
            "N": u"\u064C",  # Dammatayn
            "K": u"\u064D",  # kasratayn
            "a": u"\u064E",  # fatHa
            "u": u"\u064F",  # Damma
            "i": u"\u0650",  # kasra
            "~": u"\u0651",  # shaddah
            "o": u"\u0652",  # sukuun
            "`": u"\u0670",  # dagger 'alif
            "{": u"\u0671",  # waSla
}

uni2buck = {}
for (key, value) in buck2uni.items():
    uni2buck[value] = key


def buckwalter2unicode(inFilename, outFilename, inEnc=None, outEnc=None, reverse=0):
    if not inEnc:
        if reverse:
            inEnc = "utf_8"
        else:
            inEnc = "latin_1"

    if not outEnc:
        if reverse:
            outEnc = "latin_1"
        else:
            outEnc = "utf_8"

    try:
        outFile = codecs.open(outFilename, "w", outEnc)
    except:
        return 1

    try:
        inFile = codecs.open(inFilename, "r", inEnc)
    except:
        return 1

    lines = inFile.readlines()

    for line in lines:
        line = line.strip()
        try:
            outFile.write(transliterateString(line, reverse) + " " + os.linesep)
        except UnicodeError:
            return 1
    inFile.close()
    outFile.close()
    print("finish translating")
    return 0


def transliterateString(inString, reverse):
    out = ""
    if not reverse:
        for char in inString:
            out = out + buck2uni.get(char, char)
    else:
        for char in inString:
            out = out + uni2buck.get(char, char)
    return out


# buckwalter2unicode('E:\\dr.Zahi\\sayyed_buckwalter.txt', 'E:\\dr.Zahi\\sayyed_cleandffdff.txt', reverse=0)
