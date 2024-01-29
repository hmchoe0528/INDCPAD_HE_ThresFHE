import py_stdin
import KRD
import numpy as np

# Read from the standard input
(samples, debug_sk) = py_stdin.recover_lists(py_stdin.read_stdin())

guessed_sk = KRD.KRD(samples)

h = np.sum(np.abs(np.array(guessed_sk) - np.array(debug_sk)))

print(h)