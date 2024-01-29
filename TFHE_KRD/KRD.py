import numpy as np

# Formula of the rounding error occuring during ModSwitch
def round_error(x, k):
    return (k * round(x/k) - x)/k

def KRD(ctxt_coeff_list):
    # If N = 128, k = 2**23
    k = 2**23

    # LWE dimension
    n = len(ctxt_coeff_list[0])

    # Number of failed ciphertext
    f = len(ctxt_coeff_list)

    # Computing ModSwitch rounding errors
    round_err = [[round_error(ctxt_coeff_list[j][i], k) for i in range(n)] for j in range(len(ctxt_coeff_list))]

    round_err_avg = np.mean(round_err, axis = 0)
    
    # Empirical value for the distinguisher that lies between the two Gaussians
    alpha_over_2 = np.mean(round_err)
    guess_sk = [1 if x > alpha_over_2 else 0 for x in round_err_avg]
    return guess_sk