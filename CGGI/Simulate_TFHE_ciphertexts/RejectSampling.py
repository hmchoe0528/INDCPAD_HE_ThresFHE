import numpy as np
import scipy.special
import matplotlib.pyplot as plt
import scipy.stats

# x -> f(x) = Pr[Y+e > t-x] / < Pr[x + Y + e > t]
# rejection sampling to sample from the previous distribution
# We approximate uniform x by a Gaussian of variance 1/12
# We approximate Irwin-Hall Y by a Gaussian
def target_distribution(x, sig_x, sig_Y, sig_e, t):
    sig_Ype = np.sqrt(sig_e**2 + sig_Y**2)
    num = scipy.special.erfc(((t-x)/sig_Ype)/np.sqrt(2))
    sig_XpYpe = np.sqrt(sig_x**2 + sig_e**2 + sig_Y**2)
    dfp = scipy.special.erfc((t/sig_XpYpe)/np.sqrt(2))
    return num / dfp

def rejection_sampling(n_samples, sig_x, sig_Y, sig_e, t):
    samples = []
    M = 2  # Adjust M based on your specific case

    while len(samples) < n_samples:
        candidate = np.random.uniform(-0.5, 0.5)
        u = np.random.uniform(0, 1)

        acceptance_prob = target_distribution(candidate, sig_x, sig_Y, sig_e, t) / 2

        if u <= acceptance_prob:
            samples.append(candidate)

    return np.array(samples)

# DEBUG
DEBUG = False
if DEBUG:
    # Parameters
    sig_x = (1/12)**0.5
    sig_Y = (300/12)**0.5
    sig_e = sig_Y
    t = 7.2*(sig_Y+sig_e) # 7.2 is chosen in Noah's Ark paper for Decryption failure probability = 2^{-40}
    n_samples = 10000

    # Generate samples
    samples = rejection_sampling(n_samples, sig_x, sig_Y, sig_e, t)

    # Plot the samples
    plt.hist(samples, bins=300, density=True, alpha=0.7, label='Generated Samples')
    plt.grid()
    x_values = np.linspace(-0.5, 0.5, 1000)
    plt.plot(x_values, target_distribution(x_values, sig_x, sig_Y, sig_e, t), 'r-', label='Target Distribution')
    plt.legend()
    plt.show()
