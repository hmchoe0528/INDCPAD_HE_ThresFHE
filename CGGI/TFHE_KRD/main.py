import py_stdin
import KRD
import Distribution
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--print', action='store_true', help='plot for all in sk')
args = parser.parse_args()

# Read from the standard input
(samples, debug_sk) = py_stdin.recover_lists(py_stdin.read_stdin())

if args.print:
    Distribution.Distribution(samples)
else: 
    guessed_sk = KRD.KRD(samples)
    h = np.sum(np.abs(np.array(guessed_sk) - np.array(debug_sk)))

print(h)