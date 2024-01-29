import RejectSampling
import numpy as np
# TFHE-rs DEFAULT_Parameters derived standard deviations
sig_x = (1/12)**0.5
sig_Y = (300/12)**0.5
sig_e = sig_Y
t = 7.2*(sig_Y+sig_e)

lwe_dim = 722
q = 2**32
k = 2**23
h = np.random.binomial(lwe_dim, 0.5)


# We directly sample ciphertexts between ModSwitch and BlindRotate that fail to decrypt after ModSwitcj
f = 1000
for i in range(f):
    emsi1 = RejectSampling.rejection_sampling(h, sig_x, sig_Y, sig_e, t)
    # Generating ciphertext coefficients from the rounding error
    # For coefficients aligned with '1' in the secret key
    ai1 = np.round(emsi1 * k + np.round(np.random.randint(0, q, h)/k)*k )
    # Uniform for the others.
    ai0 = np.random.randint(0, q, lwe_dim - h)

    ai = np.concatenate([ai1, ai0]).astype(int)
    print('data: [  '+', '.join(list(map(str, ai)))+'  ]')

# Since the Key Recovery is done coefficient wise, the secret key is fixed
print('data: [  '+', '.join(['1'] * h + ['0'] * (lwe_dim - h))+'  ]')
print('data: [  '+', '.join(['1'] * h + ['0'] * (lwe_dim - h))+'  ]')
print('end')