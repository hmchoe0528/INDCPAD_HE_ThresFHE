# INDCPAD_HE_ThresFHE

This is a git repository that implements the IND-CPA-D attacks introduced in ``Attacks Against the IND-CPAD Security of Exact FHE Schemes`` written by the following authors:
Jung Hee Choeon (SNU & Crypto Lab Inc.)
Hyeongmin Choe (SNU)
Alain Passelegue (Crypto Lab Inc.)
Damien Stehlé (Crypto Lab Inc.)
Elias Suvanto (Crypto Lab Inc.)

# KRD experiments

This folder contains 5 folders concerning TFHE:
-   TFHE-rs library: An implementation of TFHE (available at https://github.com/zama-ai/tfhe-rs, commit ``ad41fdf5a5060c0a981cd0c35bf998feafe68e02``). 
-   collect\_TFHE\_ciphertexts: Rust code using TFHE-rs to run the oracle side. 
-   collected\_samples: Outputs from the above (specifically, from the custom parameter). 
-   TFHE\_KRD: Python code reading the samples (failed ciphertexts) and guessing the secret key. This is the KRD adversary side. 
-   Simulation folder to generate samples faster and for parameter sets with low decryption failure probability. 

and 2 folders about BFV KRD:
-   OpenFHE library: An implementation of many FHE schemes, in particular, BFV (available at https://github.com/openfheorg/openfhe-development, commit ``4ebb28ea7bdd894a73bc5b73e59fcfbc7825330``). 
-   BFV KRD: CPP code recovering the secret LWE error. 

## How to generate legitimate ciphertexts that fail to decrypt

There are two options:
-   Running a TFHE library: Run  ```cargo run --release > ../collected_samples/failed_ctxt.out``` inside the ```collect_TFHE_ciphertexts``` folder.
It will run the paper TFHE KRD collecting part using the ```TFHE-rs``` library.
It will use the 128-bit IND-CPA secure custom parameters. It will then put the collected ciphertexts as a text file in the ```collected_samples``` folder
-   Simulating using rejection sampling: Run  `python3 simulate_TFHE_ciphertexts/main.py > ../collected_samples/sim_failed_ctxt.out` to generate incorrect ciphertexts using a rejection sampling technique on the conditioned distribution detailed in the paper.

## How to run TFHE-KRD

Run `python3 TFHE_KRD/main.py < collected_samples/failed_ctxt.out`.
It will read the samples using ```py_stdin.py```, call `KRD.py` on them to guess the secret key and compare it to the real secret key.

## How to run BFV KRD

The C++ code is available and makes a call to the OpenFHE library. It returns the secret LWE error. 
