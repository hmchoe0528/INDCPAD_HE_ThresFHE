import re, sys

def recover_fail_lists(input_string):
    pattern_list = r'/100(.*?)Bootstrapping'
    # Matching any list
    matches_list = re.findall(pattern_list, input_string)
    print("Among", len(matches_list), "ciphertexts,")

    list_of_fail_slots_ctxt_idx = []
    list_of_fail_slots = []
    list_of_fail_slots_real_imag = []
    count = 0

    pattern_list2 = r'At (.*?): -4.927'
    for i in range(len(matches_list)):
        matches_list2 = re.findall(pattern_list2, matches_list[i])
        # print("ctxt", i, ":", len(matches_list2), "matches")
        if len(matches_list2) != 0:
            for j in range(len(matches_list2)):
                list_of_fail_slots_ctxt_idx.append(i)
                matches_list2[j] = (matches_list2[j])[-13:]
                list_of_fail_slots.append(int((matches_list2[j])[:5]))
                # print((matches_list2[j])[-5:-1])
                if (matches_list2[j])[-5:-1] == 'real':
                    list_of_fail_slots_real_imag.append(0)
                elif (matches_list2[j])[-5:-1] == 'imag':
                    list_of_fail_slots_real_imag.append(1)
            # print(matches_list2)
            count += len(matches_list2)
    print("In total of", count, "failing slots with values ~ 2^4.927")
    # print(list_of_fail_slots_ctxt_idx)
    # print(list_of_fail_slots)
    # print(list_of_fail_slots_real_imag)
    return list_of_fail_slots_ctxt_idx, list_of_fail_slots, list_of_fail_slots_real_imag

# # Read ctxts file
# with open('test', 'r') as file:
#     data = file.read().replace('\n', '')
# list_of_fail_slots_ctxt_idx, list_of_fail_slots, list_of_fail_slots_real_imag = recover_fail_lists(data)