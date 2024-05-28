import py_stdin
import KRD
import numpy as np
import sys
import math
from math import ceil, log
# for plot
import matplotlib.pyplot as plt

# ====== #
# INPUTS #
# ====== #
idx = 1
diff = 0.01
modQ = 36028797019488257

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

# # Example usage:
# input_list = [1, 2, 3, 4, 5, 6, 7, 8]
# bit_reversed_list = bit_reverse_order(input_list)
# print("Input List:", input_list)
# print("Bit-Reversed List:", bit_reversed_list)
# print("Bit-Reversed Bit-Reversed  List:", bit_reverse_order(bit_reversed_list))


###############################
# Read sk and ctxt from input #
###############################
# Read sk file
with open('long_0424_1602_sk.txt', 'r') as file:
    data_sk = file.read()
# Read ctxts file
with open('long_0424_1602_ctxt.txt', 'r') as file:
    data_ctxt = file.read().replace('\n', '')
# Reveal sk and ctxts
# (sk, ctxt_lists) = py_stdin.recover_sk_ctxt_lists(data_sk+data_ctxt)
sk, idx_sk_p1, idx_sk_m1 = py_stdin.recover_sk(data_sk)
ctxt_lists = py_stdin.recover_ctxt_lists(data_ctxt)
# Print 
N = len(sk)
print("len(sk)=", len(sk))
print("+1s:", idx_sk_p1)
print("-1s:", idx_sk_m1)
print("len(ctxt_lists[0])=", len(ctxt_lists[0]))

print("From", idx+1, "th ciphertexts..")
ctxt = [ctxt_lists[2*idx], ctxt_lists[2*idx+1]]

###############################
# Compute qI +e = c0 + c1 * s #
###############################

# Make symmetric to zero
for i in range(len(sk)):
    if  ctxt[0][i] > math.floor(modQ/2.0):
        ctxt[0][i] -= modQ
    if  ctxt[1][i] > math.floor(modQ/2.0):
        ctxt[1][i] -= modQ

# Convolution c1, s
conv = np.convolve(ctxt[1], sk)

# Subtract coefficients of degree N to 2N-2
subConv = conv[N:]
subConv = np.append(subConv, [0])
qI = (conv[0:N] - subConv)

# Add c0
qI = ctxt[0] + qI

# Normalize by q
I = qI / modQ

##############
# Plot qI +e #
##############

# Sort qI
sortedI = np.sort(I)
minI = sortedI[0]
maxI = sortedI[-1]
print("Interval for I_i: [", minI, ",", maxI, "]")
temp = minI
# Plot based on the density
axis_x = [temp]
axis_y = [0]
for i in range(len(sortedI)):
    if (sortedI[i] < temp + diff):
        axis_y[-1] += 1
    else:
        for j in range(math.floor((sortedI[i] - temp)/diff)-1):
            temp += diff
            axis_x.append(temp)
            axis_y.append(0)
        temp += diff
        axis_x.append(temp)
        axis_y.append(1)
# print("sum_y:", np.sum(axis_y))

idx_M7 = []
idx_M8 = []
idx_P7 = []
idx_P8 = []

# bit reverse
print("*Real:")
# I1=I
I1 = bit_reverse_order(I[0:int(N/2)])
for i in range(len(I1)):
    if abs(I1[i] - 7) < 0.1:
        idx_P7.append(i)
    elif abs(I1[i] - 8) < 0.1:
        idx_P8.append(i)
    elif abs(I1[i] + 7) < 0.1:
        idx_M7.append(i)
    elif abs(I1[i] + 8) < 0.1:
        idx_M8.append(i)
if len(idx_M8)!=0:
    print("near -8: ", idx_M8)
if len(idx_M7)!=0:
    print("near -7: ", idx_M7)
if len(idx_P7)!=0:
    print("near +7: ", idx_P7)
if len(idx_P8)!=0:
    print("near +8: ", idx_P8)

idx_M7 = []
idx_M8 = []
idx_P7 = []
idx_P8 = []
print("*Imag:")
# I2 = I[int(N/2):]
I2 = bit_reverse_order(I[int(N/2):])
for i in range(len(I2)):
    if abs(I2[i] - 7) < 0.1:
        idx_P7.append(i)
    elif abs(I2[i] - 8) < 0.1:
        idx_P8.append(i)
    elif abs(I2[i] + 7) < 0.1:
        idx_M7.append(i)
    elif abs(I2[i] + 8) < 0.1:
        idx_M8.append(i)
if len(idx_M8)!=0:
    print("near -8: ", idx_M8)
if len(idx_M7)!=0:
    print("near -7: ", idx_M7)
if len(idx_P7)!=0:
    print("near +7: ", idx_P7)
if len(idx_P8)!=0:
    print("near +8: ", idx_P8)
    
# Show nonzeros
print("Intervals (length", diff, ") that includes some points:")
for i in range(len(axis_x)):
    if axis_y[i]>0:
        print("(%.9f, %d)" % (axis_x[i], axis_y[i]))

plt.plot(axis_x, axis_y) 
plt.show()

# print([((np.sort((qI))[100*j])/36028797019488257.0) for j in range(int(len(qI)/100))])


# # Read from the standard input
# (samples, debug_sk) = py_stdin.recover_lists(py_stdin.read_stdin())

# guessed_sk = KRD.KRD(samples)

# h = np.sum(np.abs(np.array(guessed_sk) - np.array(debug_sk)))

# print(h)
