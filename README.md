# INDCPAD_HE_ThresFHE

This is a git repository that implements the IND-CPA-D attacks introduced in [Attacks Against the IND-CPA^D Security of Exact FHE Schemes](https://eprint.iacr.org/2024/127.pdf) written by the following authors:

Jung Hee Choeon (SNU & Crypto Lab Inc.)

Hyeongmin Choe (SNU)

Alain Passelègue (CryptoLab Inc.)

Damien Stehlé (CryptoLab Inc.)

Elias Suvanto (CryptoLab Inc.)

# Attacks Against the IND-CPA Security of Exact FHE Schemes

This repository contains the codes for the KR^D attack experiments described in the paper, and the scripts that can reproduce the figures. 

We have three main directories each corresponding to attacks against

1. BFV/BGV, implemented in [OpenFHE](https://github.com/openfheorg/openfhe-development), commit ```4ebb28ea7bdd894a73bc5b73e59fcfbc7825330```.
2. DM/CGGI, implemented in [TFHE-rs](https://github.com/zama-ai/tfhe-rs), commit ```ad41fdf5a5060c0a981cd0c35bf998feafe68e02```.
3. CKKS, implemented in [Lattigo](https://github.com/tuneinsight/lattigo), commit ```4cce9a48c1daaa2dd122921822f5ad70cd444156```.

## OpenFHE BFV iterative addition experiments

Please first install the OpenFHE library, then try the attack experiment on the parameters that the library sets by running `BFV/BFV_KRD.cpp`, which may require `cmake` or `make`. 

## TFHE-rs CGGI gate bootstrapping experiments

Please first install the TFHE-rs library, then try the attack as follows:

### Collecting failures

We collect the failing ciphertexts after gate bootstrappings by 

1) running a bunch of gate bootstrappings for a custom parameters set as

```
cd Collect_TFHE_ciphertexts
cargo run --release > ../Collected_samples/failed_ctxt.out
```

or 

2) simulating the failing ciphertexts as 

```
python3 Simulate_TFHE_ciphertexts/simulate_failures.py > ../Collected_samples/sim_failed_ctxt.out`
```

### KR^D attack

We recover the secret key from the obtained failing ciphertexts by

```
python3 TFHE_KRD/main.py < Collected_samples/failed_ctxt.out
```

or from the simulated ciphertexts ```sim_failed_ctxt.out```. 

### Helper scripts

You may try 

```
python3 TFHE_KRD/main.py --print < Collected_samples/failed_ctxt.out
```

to print out the distribution of the coefficients of the failing ciphertexts, for the secret key coefficients 0 and 1. 

## Lattigo CKKS bootstrapping experiments

Please first install the Lattigo library and modify some files from the library based on the files in the directory ```Lattigo_modified```. This is basically for 

- outputting ciphertexts before ModRaise (which do not require sk),
- outputting the secret key to evaluate the attack. 

Then try the attack for a custom parameters set with 

- K=8 (K=16 is default in Lattigo)
- Double angling constant = 0 (3 is the default in Lattigo)
- Approximation degree for cosine function = 240 (30 is the default in Lattigo)
- Hamming weight of sparse sk = 32 (32 is the default in Lattigo)
- p_fail = 0.86 ($2^{-137.7}$ is default in Lattigo)
  as follows:

### Collecting failures

We collect the failing ciphertexts after bootstrappings as

```
go run Collect_failures/collect_sk_ctxt.go > ../Collected_failures/result.out.out
```

It will output ```../Collected_failures/saved_ciphertext.out``` for the collected ciphertexts and ```../Collected_failures/skSparse_withoutNTT.out``` for the secret key. 

### KR^D attack

We recover the secret key from the obtained failing ciphertexts by

```
python3 CKKS_KRD/full_sk_recovery.py --attack
```

which will run the sk recovery attack using the ciphertexts before ModRaise, encapsulated with sparse keys. 
You can use the `--find` option to find the smallest set of candidates that perfectly includes sk. Currently, the answers to the secret key are hard-coded for inputs ```long_0424_1602...``` (from 100 runs) and ```test...``` (from 5 runs). 

### Helper scripts

#### CKKS bootstrapping failure probability

To verify the bootstrapping failure probability, try 

```
sage Irwin-Hall.sage
```

#### Distribution of qI

Try running

```
python3 CKKS_KRD/main.py
```

which will output the distribution of qI + e \approx c0 + c1*s, normalized by q. 

It will also give the index i of I, for |I_i|>7, which corresponds to the index of bootstrapping failing slots, see `0423_1200.out`, a decryption result from after bootstrapping. 

#### Distribution of a failing ciphertext

Try running 

```
python3 CKKS_KRD/full_sk_recovery.py --pos
```

which will give the coefficients distribution of the failing ciphertexts, w.r.t. the secret key coefficient of `+1`s. 
You may also try with other options such as `--neg`, `--zero`, or `--all.` 

## Collected samples

Please [download](https://drive.google.com/drive/folders/1wpzVmnKp0gS4YaF6D0r4PqBR6tvzvdca?usp=drive_link) the collected ciphertexts and secret key samples. 
Due to the large sizes, we provide an external link for downloading them. 



