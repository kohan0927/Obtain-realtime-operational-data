#coding:utf-8

def StrConvertion(strInput):
    newInput = []

    totalLen = int(len(strInput)/2)
    if len(strInput) % 2 == 1:
        totalLen = int(totalLen) + 1

    i = 0
    for num in range(totalLen):
        if len(strInput[i:i + 2]) == 2:
            tmpInput = strInput[i:i + 2][::-1]
            newInput.append(tmpInput)
            print(tmpInput)
        else:
            tmpInput = strInput[i:i+2] + '\n'
            newInput.append(tmpInput)
            print(tmpInput)

        i = i + 2

    finalInput = ''.join(newInput)

    return finalInput
