import py_stdin
import KRD
import numpy as np
import matplotlib.pyplot as plt
# Read from the standard input
(samples, debug_sk) = py_stdin.recover_lists(py_stdin.read_stdin())

f = 10000
scores = []
for k in range(0, 1+int(np.log(f)/np.log(2))):
    i=2**k

    guessed_sk = KRD.KRD(samples[:i])
    scores.append(np.sum(abs(np.array(debug_sk)-np.array(guessed_sk))))

print(scores[1::100])
plt.title('CRASH')
plt.grid()
plt.plot(scores)
plt.ylabel('# mismatches')
plt.xlabel('log2( of number of failures)')
plt.title("Performances of the KRD depending on the number of samples")

plt.show()