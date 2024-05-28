import py_stdin
import KRD
import py_recover
import numpy as np
import sys
import math
from math import ceil, log
# for plot
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--pos', action='store_true', help='plot for +1s in sk')
parser.add_argument('--neg', action='store_true', help='plot for -1s in sk')
parser.add_argument('--zero', action='store_true', help='plot for 0s in sk')
parser.add_argument('--all', action='store_true', help='plot for all sk')
parser.add_argument('--attack', action='store_true', help='attack, recovering sk')
parser.add_argument('--find', action='store_true', help='attack, find the smallest k, where the top k candidates includes sk')
args = parser.parse_args()

# ====== #
# Inputs #
# ====== #
# N: ring degree
N = 2**16
# ctxt_idx: which ctxt will we use?
ctxt_idx = 1
# modQ: modulus in the bottom
modQ = 36028797019488257
# interval length for plot
diff = 1/8.0
# threshold for +1 or -1
# one can set this to any positive number, but too large threshold will give less sk candidates.
threshold = 0.09

# idx of sk for +1s
if args.pos:
    # test
    # input_sk = [8449, 9194, 10650, 10891, 17623, 18417, 19200, 21912, 21940, 22422, 23431, 25804, 33028, 40718, 41422, 43573, 47619, 54921] 
    # long_0424_1602
    # input_sk = [3449, 4499, 4694, 13090, 18513, 21257, 23341, 25487, 26361, 35741, 42455, 47593, 58280, 61523, 62304, 63489, 63729, 63781, 63783]
    input_sk = [3449, 4499, 4694, 13090, 18513]
    input_sk_all = [input_sk]
    leg = ['s= 1']
# idx of sk for -1s
if args.neg:
    # test
    # input_sk = [4601, 8146, 9923, 12798, 16188, 25607, 26136, 30084, 33562, 39203, 46088, 48356, 50580, 61305]
    # long_0424_1602
    # input_sk = [32, 4197, 5690, 9691, 13523, 15167, 23557, 30742, 30782, 42497, 57969, 61762, 62972]
    input_sk = [32, 4197, 5690, 9691, 13523]
    input_sk_all = [input_sk]
    leg = ['s= -1']
# idx of sk for 0s, from 0 to 100
if args.zero:
    input_sk = range(5)
    input_sk_all = [input_sk]
    leg = ['s= 0']
if args.all:
    input_sk_all = [[3449, 4499, 4694, 13090, 18513, 21257, 23341, 25487, 26361, 35741], [32, 4197, 5690, 9691, 13523, 15167, 23557, 30742, 30782, 42497], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
    leg = ['z = 1', 'z = -1', 'z = 0']
    # print(len(input_sk_all))
ATK = False
if args.attack:
    # long_0424_1602
    input_sk_pos = [3449, 4499, 4694, 13090, 18513, 21257, 23341, 25487, 26361, 35741, 42455, 47593, 58280, 61523, 62304, 63489, 63729, 63781, 63783]
    input_sk_neg = [32, 4197, 5690, 9691, 13523, 15167, 23557, 30742, 30782, 42497, 57969, 61762, 62972]
    ATK = True

# ================= #
# Bit reversing map #
# ================= #
# bit_reverse_order
def bit_reverse_order(input_list):
    n = len(input_list)
    num_bits = ceil(log(n, 2))
    bit_reversed_indices = [0] * n
    for i in range(n):
        rev_i = 0
        for j in range(num_bits):
            if (i >> j) & 1:
                rev_i |= 1 << (num_bits - 1 - j)
        bit_reversed_indices[i] = rev_i
    bit_reversed_list = [input_list[index] for index in bit_reversed_indices]
    return bit_reversed_list

# make a bit reversing map
input_list = range(2**15)
bit_reversing_map = bit_reverse_order(input_list)

# =============== #
# Read and adjust #
# =============== #
print("\nReading from the results..")
# Read decryption results
# with open('../Collected_failures/test.out', 'r') as file:
# with open('../Collected_failures/long_0424_1602.out', 'r') as file:
with open('../Collected_failures/result.out', 'r') as file:
    data = file.read().replace('\n', '')
list_ctxt_idx_per_slot_fail, list_fail_slots, list_fail_slots_real_imag = py_recover.recover_fail_lists(data)
# ctxt idx for each failing slots & filing slot idx in each ciphertexts & real vs. imag
# list_ctxt_idx_per_slot_fail = [0, 0, 0, 1, 3, 5, 5, 5, 7, 7, 8, 8, 9, ...
# list_fail_slots =             [4731, 9429, 21626, 21327, 27514, 18190, 19510, 21760, ...
# list_fail_slots_real_imag =   [1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, ...

# Read ctxts
# with open('../Collected_failures/test_ctxt.out', 'r') as file:
# with open('../Collected_failures/long_0424_1602_ctxt.out', 'r') as file:
with open('../Collected_failures/saved_ciphertext.out', 'r') as file:
    data_ctxt = file.read().replace('\n', '')
# Reveal ctxts
ctxt_lists = py_stdin.recover_ctxt_lists(data_ctxt)

# in case of shortened ctxt list, we delete some from the lists
here = int(len(ctxt_lists)/2)
if int(len(ctxt_lists)/2) <= list_ctxt_idx_per_slot_fail[-1]:
    for i in range(len(list_ctxt_idx_per_slot_fail)):
        if int(len(ctxt_lists)/2) <= list_ctxt_idx_per_slot_fail[i]:
            here = i-1
            break
list_ctxt_idx_per_slot_fail = list_ctxt_idx_per_slot_fail[:here]
list_fail_slots = list_fail_slots[:here]
list_fail_slots_real_imag = list_fail_slots_real_imag[:here]
print("We only use", len(list_ctxt_idx_per_slot_fail), "ciphertexts")

print("Done!")

if not ATK:
    # axis_yy = []
    fig, ax = plt.subplots()
    for l in range(len(input_sk_all)):
        input_sk = input_sk_all[l]
        # ============================= #
        # Collect coefficients using sk #
        # ============================= #
        # We first collect the coefficients of the ciphertexts
        # corresponfding to the failed slots and sk
        collect_coeff_list = []
        for j in range(len(list_ctxt_idx_per_slot_fail)):
            input_fail_coeff = list_fail_slots[j]
            input_fail_real_imag = list_fail_slots_real_imag[j]
            ctxt = ctxt_lists[2*list_ctxt_idx_per_slot_fail[j]+1]
            # Make symmetric to zero
            for i in range(len(ctxt)):
                if  ctxt[i] > math.floor(modQ/2.0):
                    ctxt[i] -= modQ
            input_fail_coeff = [bit_reversing_map[input_fail_coeff]]
            idx_fail_list = [input_fail_coeff[0] + int(N/2)*input_fail_real_imag]

            coeff_list = []
            for idx_fail in idx_fail_list:
                for idx_sk in input_sk:
                    if (idx_fail >= idx_sk):
                        idx_temp = idx_fail - idx_sk
                        coeff_list.append(ctxt[idx_temp])
                    else:
                        idx_temp = idx_fail - idx_sk + N
                        coeff_list.append(-ctxt[idx_temp])
            collect_coeff_list = np.concatenate((collect_coeff_list, coeff_list), axis=None)

        # ======== #
        # for Plot #
        # ======== #
        sorted_collect_coeff_list = np.sort(collect_coeff_list)/modQ

        min_collect_coeff = sorted_collect_coeff_list[0]
        max_collect_coeff = sorted_collect_coeff_list[-1]
        print("Interval: [", min_collect_coeff, ",", max_collect_coeff, "]")
        temp = -0.5
        # Plot based on the density
        axis_x = [temp]
        axis_y = [0]
        for i in range(len(sorted_collect_coeff_list)):
            if (sorted_collect_coeff_list[i] < temp + diff):
                axis_y[-1] += 1
            else:
                for j in range(math.floor((sorted_collect_coeff_list[i] - temp)/diff)-1):
                    temp += diff
                    axis_x.append(temp)
                    axis_y.append(0)
                temp += diff
                axis_x.append(temp)
                axis_y.append(1)
        print("Total number of used failures:", np.sum(axis_y))
        print("Averaged:", np.average(sorted_collect_coeff_list))

        axis_x = [axis_x[i] + diff/2.0 for i in range(len(axis_x))]
        lines1, = ax.plot(axis_x, axis_y, label=leg[l])
    plt.gca().set_xlim([-0.5, 0.5])
    plt.gca().set_ylim(bottom=0)
    plt.figlegend(loc="upper center", fontsize="20")
    plt.xlabel("c "+r'$\in$'+" [-0.5, 0.5]", fontsize="20")
    # plt.ylabel("Number of c", fontsize="15")
    fig.tight_layout()
    plt.show()
else:
    print("\nMaking a shorter ctxt list..")
    estimated_sk_pos = []
    estimated_sk_neg = []
    estimated_sk_pos_avg = []
    estimated_sk_neg_avg = []
    avg_list = []
    idx_list = []
    ctxt_shorter_list = []

    # make a shortened ctxt list
    for j in range(len(list_ctxt_idx_per_slot_fail)):
        if (j==0) or list_ctxt_idx_per_slot_fail[j] != list_ctxt_idx_per_slot_fail[j-1]:
            ctxt = ctxt_lists[2*list_ctxt_idx_per_slot_fail[j]+1]
            # Make symmetric to zero
            for i in range(len(ctxt)):
                ctxt[i] = ctxt[i] / modQ
                if  ctxt[i] > 0.5:
                    ctxt[i] -= 1.0
            ctxt_shorter_list.append(ctxt)
    print("Done!\n\nCollecting sample..")

    # collect the coefficients
    for k in range(N):
        # ============================ #
        # Collect coefficients using k #
        # ============================ #
        collect_coeff_list = []
        ctxt_idx_temp = 0
        for j in range(len(list_ctxt_idx_per_slot_fail)):
            input_fail_coeff = list_fail_slots[j]
            input_fail_real_imag = list_fail_slots_real_imag[j]
            input_fail_coeff = bit_reversing_map[input_fail_coeff]
            idx_fail = input_fail_coeff + int(N/2)*input_fail_real_imag

            if (j==0) or list_ctxt_idx_per_slot_fail[j] != list_ctxt_idx_per_slot_fail[j-1]:
                ctxt = ctxt_shorter_list[ctxt_idx_temp]
                ctxt_idx_temp += 1

            coeff_list = []
            if (idx_fail >= k):
                idx_temp = idx_fail - k
                coeff_list.append(ctxt[idx_temp])
            else:
                idx_temp = idx_fail - k + N
                coeff_list.append(-ctxt[idx_temp])
            collect_coeff_list = np.concatenate((collect_coeff_list, coeff_list), axis=None)
        # we averaeg
        # avg = np.average(collect_coeff_list)
        # we instead average the largest half coefficients
        avg2 = np.average(np.sort(collect_coeff_list)[-int(len(collect_coeff_list)/2)])
        avg_list.append(avg2)
        # if k%1000 == 0:
        #     print(str(k)+"..", end="")
        #     if (k%10000 == 0) and (k != 0):
        #         print("")

        if avg2 > threshold:
            # print("\navg > 0.1:", k)
            estimated_sk_pos.append(k)
            estimated_sk_pos_avg.append(avg2)
        elif avg2 < -threshold:
            # print("\navg < -0.1:", k)
            estimated_sk_neg.append(k)
            estimated_sk_neg_avg.append(avg2)
    print("Done!")

    # Choose the 32 indices among the candidates
    # One may try NumEstimate = 40 or larger
    NumEstimateBound = 33
    if args.find:
        NumEstimateBound = 64
    estimated_sk_neg_avg_temp = [-estimated_sk_neg_avg[i] for i in range(len(estimated_sk_neg_avg))]
    for NumEstimate in range(32, NumEstimateBound, 1):
        print("\n***\nNumEstimate: ", NumEstimate)

        all_together = np.concatenate((estimated_sk_pos_avg, estimated_sk_neg_avg_temp), axis=None)
        selected_estimated_sk_pos = []
        selected_estimated_sk_neg = []
        all_together = np.sort(all_together)
        for i in range(NumEstimate):
            for j in range(len(estimated_sk_pos_avg)):
                if estimated_sk_pos_avg[j] == all_together[-i]:
                    selected_estimated_sk_pos.append(estimated_sk_pos[j])
            for j in range(len(estimated_sk_neg_avg_temp)):
                if estimated_sk_neg_avg_temp[j] == all_together[-i]:
                    selected_estimated_sk_neg.append(estimated_sk_neg[j])
        selected_estimated_sk_pos = np.sort(selected_estimated_sk_pos)
        selected_estimated_sk_neg = np.sort(selected_estimated_sk_neg)

        # score the attack
        score = 0
        for value in selected_estimated_sk_pos:
            if value in input_sk_pos:
                score += 1
        for value in selected_estimated_sk_neg:
            if value in input_sk_neg:
                score += 1

        print("\nEstimated sk +1 ("+str(len(selected_estimated_sk_pos))+") :", selected_estimated_sk_pos.tolist())
        print("Real      sk +1 ("+str(len(input_sk_pos))+") :", input_sk_pos)
        print("\nEstimated sk -1 ("+str(len(selected_estimated_sk_neg))+") :", selected_estimated_sk_neg.tolist())
        print("Real      sk -1 ("+str(len(input_sk_neg))+") :", input_sk_neg)
        print("Score:", score)
        if score == 32:
            break
