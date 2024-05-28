import re, sys

# Just to read the whole input as one string from standard input 
def read_stdin():
    buffer = ''
    while True:
        line = sys.stdin.readline().rstrip('\n')
        if 'end' in line:
            break
        else:
            buffer += line
    return buffer

def recover_lists(input_string):
    # Regular expression pattern any list in the string
    pattern_list = r'data: \[(.*?)\]'
    # Matching any list
    matches_list = re.findall(pattern_list, input_string)
    # Converting all matched strings to a list of integer lists
    ctxt_coeff_list = []
    for ma in matches_list[:-2]:
        ctxt_coeff_list.append(eval('[' + ma + ']'))
    
    # DEBUG purpose: Recovering the secret key SK
    SK = eval('[' + matches_list[-2] + ']')
    return (ctxt_coeff_list, SK)