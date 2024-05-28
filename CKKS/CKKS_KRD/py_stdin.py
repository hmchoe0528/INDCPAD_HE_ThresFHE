import re, sys

# Just read the whole input as one string from the standard input 
def read_stdin():
    buffer = ''
    while True:
        line = sys.stdin.readline().rstrip('\n')
        if 'end' in line:
            break
        else:
            buffer += line
    return buffer

def recover_sk_ctxt_lists(input_string):
    # print(len(input_string))

    # Regular expression pattern any list in the string
    # sk:   {"{[[" ... "]]}" 
    # ctxt: ["{[[" ... "]]}" {[[...]]}]} ...
    pattern_list = r'{\[\[(.*?)\]\]}'
    # Matching any list
    matches_list = re.findall(pattern_list, input_string)
    print("*Input: sk with", int(len(matches_list)/2), "ciphertext!")
    # print(len(matches_list), ":", [len(matches_list[i]) for i in range(len(matches_list))])

    # Split
    split_list = (matches_list[0]).split()

    # Recovering the secret key SK
    SK = [int(split_list[i]) for i in range(len(split_list))]
    # Debug-purpose
    # print(len(SK))
    countP1 = 0
    countM1 = 0
    idxP1 = []
    idxM1 = []
    for i in range(len(SK)):
        if SK[i] > 1:
            SK[i] = -1
            # print("-1's index",i)
            countM1 += 1
            idxM1.append(i)
        elif SK[i] == 1:
            # print("1's index",i)
            countP1 += 1
            idxP1.append(i)
    print("*HWT(sk):", countP1+countM1, "=", countP1, "+", countM1)

    # Recovering the ctxt coeffs
    split_list = [(matches_list[i]).split() for i in range(1, len(matches_list))]
    # print(len(CTXT_list), ":", [len(CTXT_list[i]) for i in range(len(CTXT_list))])
    CTXT_list = [[int(split_list[i][j]) for j in range(len(split_list[0]))] for i in range(len(split_list))]
    # print(CTXT_list[0][10])
    return SK, CTXT_list

def recover_ctxt_lists(input_string):
    # print(len(input_string))

    # Regular expression pattern any list in the string
    # ctxt: ["{[[" ... "]]}" {[[...]]}]} ...
    pattern_list = r'{\[\[(.*?)\]\]}'
    # Matching any list
    matches_list = re.findall(pattern_list, input_string)
    # print(int(len(matches_list)/2), "ciphertext!")
    # print(len(matches_list), ":", [len(matches_list[i]) for i in range(len(matches_list))])

    # Split
    split_list = (matches_list[0]).split()

    # Recovering the ctxt coeffs
    split_list = [(matches_list[i]).split() for i in range(len(matches_list))]
    # print(len(CTXT_list), ":", [len(CTXT_list[i]) for i in range(len(CTXT_list))])
    CTXT_list = [[int(split_list[i][j]) for j in range(len(split_list[0]))] for i in range(len(split_list))]
    # print(CTXT_list[0][10])
    return CTXT_list
    
def recover_sk(input_string):
    # Regular expression pattern any list in the string
    # "{{[[" ... "]]}"" ...
    pattern_list = r'{{\[\[(.*?)\]\]}'
    # Matching any list
    matches_list = re.findall(pattern_list, input_string)
    # Split
    split_list = (matches_list[0]).split()

    # Recovering the secret key SK
    SK = [int(split_list[i]) for i in range(len(split_list))]
    # Debug-purpose
    # print(len(SK))
    countP1 = 0
    countM1 = 0
    idxP1 = []
    idxM1 = []
    for i in range(len(SK)):
        if SK[i] > 1:
            SK[i] = -1
            # print("-1's index",i)
            countM1 += 1
            idxM1.append(i)
        elif SK[i] == 1:
            # print("1's index",i)
            countP1 += 1
            idxP1.append(i)
    # print("SK HWT:", countP1+countM1, "=", countP1, "+", countM1)

    return (SK, idxP1, idxM1)



