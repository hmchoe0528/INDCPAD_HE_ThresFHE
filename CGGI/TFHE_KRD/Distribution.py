import numpy as np
import math
# for plot
import matplotlib.pyplot as plt

# Formula of the rounding error occuring during ModSwitch
def round_error(x, k):
    return (k * round(x/k) - x)/k

def Distribution(ctxt_coeff_list):
    # If N = 128, k = 2**23
    k = 2**23

    # LWE dimension
    n = len(ctxt_coeff_list[0])

    # Number of failed ciphertext
    f = len(ctxt_coeff_list)

    # Computing ModSwitch rounding errors
    diff=1/8.0

    fig, ax = plt.subplots()

    idx = [[1, 4, 7, 8, 11, 12, 13, 14, 16, 20], [0, 2, 3, 5, 6, 9, 10, 15, 17, 18]]
    leg = ['z=1', 'z=0']
    # for i in [1, 4, 7, 8, 11, 12, 13, 14, 16, 20, 21, 22, 24, 25]:

    for l in range(2):
        round_err = []
        for i in idx[l]:
        # for i in [0, 2, 3, 5, 6, 9, 10, 15, 17, 18, 19, 23, 26]:
            round_err_temp = [round_error(ctxt_coeff_list[j][i], k) for j in range(len(ctxt_coeff_list))]
            round_err = np.concatenate((round_err, round_err_temp), axis=None)
            #  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26
            # [0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0
            # round_err_avg = np.mean(round_err)
            
            # Empirical value for the distinguisher that lies between the two Gaussians
            # alpha_over_2 = np.mean(round_err)
            
        # Sort qI
        sortedI = np.sort(round_err)
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
        axis_x = [axis_x[i] + diff/2.0 for i in range(len(axis_x))]
        # axis_y = [axis_y[i]/100 for i in range(len(axis_y))]
        ax.plot(axis_x, axis_y, label=leg[l])
    plt.gca().set_xlim([-0.5, 0.5])
    plt.gca().set_ylim([7000, 13000])
    plt.figlegend(loc="upper center", fontsize="20")
    plt.xlabel("c "+r'$\in$'+" [-0.5, 0.5]", fontsize="20")
    plt.ylabel("Number of c", fontsize="20")
    fig.tight_layout()
    plt.show()
    return 0