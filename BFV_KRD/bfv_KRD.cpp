//==================================================================================
// BSD 2-Clause License
//
// Copyright (c) 2014-2022, NJIT, Duality Technologies Inc. and other contributors
//
// All rights reserved.
//
// Author TPOC: contact@openfhe.org
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice, this
//    list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
// OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//==================================================================================

/*
  Simple example for BFVrns (integer arithmetic)
 */

#include "openfhe.h"

using namespace lbcrypto;

void EvalNoiseBFV(PrivateKey<DCRTPoly> privateKey, ConstCiphertext<DCRTPoly> ciphertext, usint ptm,
                  double& noise, double& logQ);

int main() {
    CCParams<CryptoContextBFVRNS> parameters;
    uint64_t ptm = 65537;
    parameters.SetPlaintextModulus(ptm);
    parameters.SetMultiplicationTechnique(HPSPOVERQ);  // BEHZ, HPS, HPSPOVERQ, HPSPOVERQLEVELED
    parameters.SetMultiplicativeDepth(0);             // 50, 100, 150
    
    parameters.SetSecurityLevel(SecurityLevel::HEStd_128_classic);

    CryptoContext<DCRTPoly> cryptoContext = GenCryptoContext(parameters);
    // Enable features that you wish to use
    cryptoContext->Enable(PKE);
    cryptoContext->Enable(KEYSWITCH);
    cryptoContext->Enable(LEVELEDSHE);

    // Initialize Public Key Containers
    KeyPair<DCRTPoly> keyPair;

    // Generate a public/private key pair
    keyPair = cryptoContext->KeyGen();

    // A plaintext vector is encoded
    std::vector<int64_t> vectorOfInts1 = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,};
    Plaintext plaintext1               = cryptoContext->MakeCoefPackedPlaintext(vectorOfInts1);

    // The encoded vector ise encrypted
    auto ciphertext1 = cryptoContext->Encrypt(keyPair.publicKey, plaintext1);

    // Homomorphic Add
    auto ciphertextAdd12 = cryptoContext->EvalAdd(ciphertext1, ciphertext1);
    int tt = 43;
    for (auto i=0;i<tt;i++)
        ciphertextAdd12 = cryptoContext->EvalAdd(ciphertextAdd12, ciphertextAdd12);

    // Decrypt the result of the addition
    Plaintext plaintextAddResult;
    cryptoContext->Decrypt(keyPair.secretKey, ciphertextAdd12, &plaintextAddResult);

    double noise = 0, logQ = 0;
    
    std::cout << "Outputting the secret noise of the initial ciphertexts" << std::endl;
    EvalNoiseBFV(keyPair.secretKey, ciphertext1, ptm, noise, logQ);

    std::cout << "Outputting the plaintext of the final ciphertext" << std::endl;
    std::cout << "#1 + #1: " << plaintextAddResult << std::endl;
    return 0;
}

void EvalNoiseBFV(PrivateKey<DCRTPoly> privateKey, ConstCiphertext<DCRTPoly> ciphertext, usint ptm,
                  double& noise, double& logQ) {
    const auto cryptoParams = std::static_pointer_cast<CryptoParametersBFVRNS>(privateKey->GetCryptoParameters());

    const std::vector<DCRTPoly>& cv = ciphertext->GetElements();
    DCRTPoly s                      = privateKey->GetPrivateElement();

    size_t sizeQl = cv[0].GetParams()->GetParams().size();
    size_t sizeQs = s.GetParams()->GetParams().size();

    size_t diffQl = sizeQs - sizeQl;

    auto scopy(s);
    scopy.DropLastElements(diffQl);

    DCRTPoly sPower(scopy);

    DCRTPoly b = cv[0];
    b.SetFormat(Format::EVALUATION);

    DCRTPoly ci;
    for (size_t i = 1; i < cv.size(); i++) {
        ci = cv[i];
        ci.SetFormat(Format::EVALUATION);

        b += sPower * ci;
        sPower *= scopy;
    }

    DCRTPoly res;
    res = b;// - plain;

    // Converts back to coefficient representation
    res.SetFormat(Format::COEFFICIENT);
    noise        = (log2(res.Norm()));;
    for (uint i=0;i<100;i++) {
        auto x = res.GetElementAtIndex(0).GetValues()[i];
        if (2*x < res.GetModulus().ConvertToInt())
            std::cout << x << " ";
        else
            std::cout << "-" << res.GetModulus().ConvertToInt()-x << " ";
    }
    std::cout << std::endl;
}
