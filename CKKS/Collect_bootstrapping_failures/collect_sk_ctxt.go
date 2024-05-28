// Modified from examples/singe_party/applications/reals_bootstrapping_slim/main.go
//
// This example instantiates a custom order of the circuit evaluating:
//
// Step 1) SlotsToCoeffs: Homomorphic Decoding
// Step 2) ScaleDown: Scale the ciphertext to q0/|m|
// Step 3) ModUp: Raise modulus from q0 to qL
// Step 3-1) Sparse Encapsulation -> should print after this
// Step 3-2) ModUp
// Step 3-3) Sparse Decapsulation
// Step 4) CoeffsToSlots: Homomorphic encoding
// Step 5) EvalMod (and to back to 0): Homomorphic modular reduction
//
// Use the flag -short to run the examples fast but with insecure parameters.
package main

import (
	"bufio"
	"flag"
	"fmt"
	"math"
	"math/big"
	"os"
	"time"

	"github.com/tuneinsight/lattigo/v5/core/rlwe"
	"github.com/tuneinsight/lattigo/v5/he/hefloat"
	"github.com/tuneinsight/lattigo/v5/he/hefloat/bootstrapping"
	"github.com/tuneinsight/lattigo/v5/ring"
)

// Short flag
var flagShort = flag.Bool("short", false, "run the example with a smaller and insecure ring degree.")

// ======//
// main //
// ======//
func main() {

	start := time.Now()
	// Short flag
	flag.Parse()
	// Default LogN, which with the following defined parameters
	// provides a security of 128-bit.
	LogN := 16
	if *flagShort {
		LogN -= 3
	}
	// NumIter
	NumIter := 40

	//============================
	//=== 1) SCHEME PARAMETERS ===
	//============================
	LogDefaultScale := 40

	q0 := []int{55}                                    // 2) ScaleDown & 3) ModUp
	qiSlotsToCoeffs := []int{39, 39, 39}               // 1) SlotsToCoeffs
	qiEvalMod := []int{60, 60, 60, 60, 60, 60, 60, 60} // 5) EvalMod
	qiCoeffsToSlots := []int{56, 56, 56, 56}           // 4) CoeffsToSlots

	LogQ := append(q0, qiSlotsToCoeffs...)
	LogQ = append(LogQ, qiEvalMod...)
	LogQ = append(LogQ, qiCoeffsToSlots...)

	params, err := hefloat.NewParametersFromLiteral(hefloat.ParametersLiteral{
		LogN:            LogN,                      // Log2 of the ring degree
		LogQ:            LogQ,                      // Log2 of the ciphertext modulus
		LogP:            []int{61, 61, 61, 61, 61}, // Log2 of the key-switch auxiliary prime moduli
		LogDefaultScale: LogDefaultScale,           // Log2 of the scale
		Xs:              ring.Ternary{H: 192},
	})
	if err != nil {
		panic(err)
	}

	// Show the Q0, ctxt modulus after S2C
	fmt.Println("\nQ0 (after S2C):", (params.Q())[0])

	//====================================
	//=== 2) BOOTSTRAPPING PARAMETERS ===
	//====================================

	// CoeffsToSlots parameters (homomorphic encoding)
	CoeffsToSlotsParameters := hefloat.DFTMatrixLiteral{
		Type:         hefloat.HomomorphicEncode,
		Format:       hefloat.RepackImagAsReal, // Returns the real and imaginary part into separate ciphertexts
		LogSlots:     params.LogMaxSlots(),
		LevelStart:   params.MaxLevel(),
		LogBSGSRatio: 1,
		Levels:       []int{1, 1, 1, 1}, //qiCoeffsToSlots
	}

	// Parameters of the homomorphic modular reduction x mod 1
	Mod1ParametersLiteral := hefloat.Mod1ParametersLiteral{
		LogScale: 60,                  // Matches qiEvalMod
		Mod1Type: hefloat.CosDiscrete, // Multi-interval Chebyshev interpolation
		// Modified params below
		// With Mod1Degree=240, DoubleAngle=0, K=8, it fails at several slots on average.
		// K=7 (0.000015 per slot, 		0.862 per ctxt)
		// K=8 (0.00000058 per slot, 	0.074 per ctxt)
		// K=9 (0.00000000126 per slot,	0.0016 per ctxt)
		Mod1Degree:      240, // Depth 8 instead of 5 (default: 30)
		DoubleAngle:     0,   // Depth 0 instead of 3 (default: 3)
		K:               7,   // (default: 16) With EphemeralSecretWeight = 32 and 2^{15} slots, ensures < 2^{-138.7} failure probability
		LogMessageRatio: 5,   // q/|m| = 2^5
		Mod1InvDegree:   0,   // Depth 0
		LevelStart:      params.MaxLevel() - len(CoeffsToSlotsParameters.Levels),
	}

	// Since we scale the values by 1/2^{LogMessageRatio} during CoeffsToSlots,
	// we must scale them back by 2^{LogMessageRatio} after EvalMod.
	// This is done by scaling the EvalMod polynomial coefficients by 2^{LogMessageRatio}.
	Mod1ParametersLiteral.Scaling = math.Exp2(-float64(Mod1ParametersLiteral.LogMessageRatio))

	// SlotsToCoeffs parameters (homomorphic decoding)
	SlotsToCoeffsParameters := hefloat.DFTMatrixLiteral{
		Type:         hefloat.HomomorphicDecode,
		LogSlots:     params.LogMaxSlots(),
		Scaling:      new(big.Float).SetFloat64(math.Exp2(float64(Mod1ParametersLiteral.LogMessageRatio))),
		LogBSGSRatio: 1,
		Levels:       []int{1, 1, 1}, // qiSlotsToCoeffs
	}

	SlotsToCoeffsParameters.LevelStart = len(SlotsToCoeffsParameters.Levels)

	// Custom bootstrapping.Parameters.
	// All fields are public and can be manually instantiated.
	btpParams := bootstrapping.Parameters{
		ResidualParameters:      params,
		BootstrappingParameters: params,
		SlotsToCoeffsParameters: SlotsToCoeffsParameters,
		Mod1ParametersLiteral:   Mod1ParametersLiteral,
		CoeffsToSlotsParameters: CoeffsToSlotsParameters,
		EphemeralSecretWeight:   32, // > 128bit secure for LogN=16 and LogQP = 115.
		CircuitOrder:            bootstrapping.DecodeThenModUp,
	}

	if *flagShort {
		// Corrects the message ratio Q0/|m(X)| to take into account the smaller number of slots and keep the same precision
		btpParams.Mod1ParametersLiteral.LogMessageRatio += 16 - params.LogN()
	}

	// We pring some information about the bootstrapping parameters (which are identical to the residual parameters in this example).
	// We can notably check that the LogQP of the bootstrapping parameters is smaller than 1550, which ensures
	// 128-bit of security as explained above.
	fmt.Printf("Bootstrapping parameters: logN=%d, logSlots=%d, H(%d; %d), sigma=%f, logQP=%f, levels=%d, scale=2^%d\n",
		btpParams.BootstrappingParameters.LogN(),
		btpParams.BootstrappingParameters.LogMaxSlots(),
		btpParams.BootstrappingParameters.XsHammingWeight(),
		btpParams.EphemeralSecretWeight,
		btpParams.BootstrappingParameters.Xe(),
		btpParams.BootstrappingParameters.LogQP(),
		btpParams.BootstrappingParameters.QCount(),
		btpParams.BootstrappingParameters.LogDefaultScale())

	//===========================
	//=== 3) KEYGEN & ENCRYPT ===
	//===========================

	// Now that both the residual and bootstrapping parameters are instantiated, we can
	// instantiate the usual necessary object to encode, encrypt and decrypt.

	// Scheme context and keys
	// keygenerator
	kgen := rlwe.NewKeyGenerator(params)
	// keygen
	sk, pk := kgen.GenKeyPairNew()
	// encoder, decoder, encryptor, decryptor
	encoder := hefloat.NewEncoder(params)
	decryptor := rlwe.NewDecryptor(params, sk)
	encryptor := rlwe.NewEncryptor(params, pk)
	// keygen BTS keys
	fmt.Println()
	fmt.Println("Generating bootstrapping evaluation keys...")
	// skSparse,
	evk, _, err := btpParams.GenEvaluationKeys(sk)
	if err != nil {
		panic(err)
	}
	// fmt.Println(skSparse.BinarySize())
	// decryptorSparse := rlwe.NewDecryptor(params, skSparse)
	fmt.Println("Done")

	//========================
	//=== 4) BOOTSTRAPPING ===
	//========================

	// Instantiates the bootstrapper
	var eval *bootstrapping.Evaluator
	if eval, err = bootstrapping.NewEvaluator(btpParams, evk); err != nil {
		panic(err)
	}

	// Prepare saving the ciphertexts
	f, err := os.Create("../Collected_failures/saved_ciphertext.txt")
	if err != nil {
		panic(err)
	}
	defer f.Close()
	w := bufio.NewWriter(f)

	elapsed := time.Since(start)
	fmt.Printf("******\nAll the settings took %s\n******\n", elapsed)
	start2 := time.Now()

	// =============== //
	//   For msg = 0   //
	// iterate NumIter //
	// =============== //

	for i := 0; i < NumIter; i++ {

		// Generate plaintext
		valuesWant := make([]complex128, params.MaxSlots())
		for i := range valuesWant {
			valuesWant[i] = 0 + 0i
			// valuesWant[i] = 1 + 0i
		}
		// for i := 1; i < 10; i++ {
		// 	valuesWant[2*i] = valuesWant[i-1] + 1
		// 	fmt.Println(2*i, ":", valuesWant[2*i])
		// }

		// Prepare encrypting at the starting level of SlotsToCoeffs
		plaintext := hefloat.NewPlaintext(params, SlotsToCoeffsParameters.LevelStart)
		if err := encoder.Encode(valuesWant, plaintext); err != nil {
			panic(err)
		}

		// Encrypt
		ciphertext, err := encryptor.EncryptNew(plaintext)
		if err != nil {
			panic(err)
		}

		valuesTest := valuesWant

		// =========== //
		// BTS starts! //
		// =========== //

		fmt.Printf("Bootstrapping...%d/%d for msg=0: ", i+1, NumIter)
		//-----
		// Step 0: nothing, just print levels..
		// Show Lvl., LogQ, Scale factor for debugging.
		// fmt.Printf("\n0) Level: %d (logQ = %d), Scale: 2^%f", ciphertext.Level(), params.LogQLvl(ciphertext.Level()), math.Log2(ciphertext.Scale.Float64()))

		//-----
		// Step 1: SlotsToCoeffs (Homomorphic decoding)
		if ciphertext, err = eval.SlotsToCoeffs(ciphertext, nil); err != nil {
			panic(err)
		}
		// Show Lvl., LogQ, Scale factor for debugging.
		// fmt.Printf("\n1) Level: %d (logQ = %d), Scale: 2^%f", ciphertext.Level(), params.LogQLvl(ciphertext.Level()), math.Log2(ciphertext.Scale.Float64()))
		// Show the decryption result of S2C(ciphertext), which will appoximately valuesWant:
		// Decode(0s) = 0 polynomial.
		// fmt.Println("\nAfter S2C: ")
		// printDebug(params, ciphertext, valuesTest, decryptor, encoder)
		// _, err = fmt.Fprintln(w, "Ciphertext (", i, "th) for msg=0: ", ciphertext.Element)
		// if err != nil {
		// 	panic(err)
		// }
		//-----
		// Step 2: scale to q/|m|
		ciphertext2, _, err := eval.ScaleDown(ciphertext)
		if err != nil {
			panic(err)
		}
		// fmt.Println("\nAfter ScaleDown: ")
		// printDebug(params, ciphertext2, valuesTest, decryptor, encoder)
		// Show Lvl., LogQ, Scale factor for debugging.
		// fmt.Printf("\n2) Level: %d (logQ = %d), Scale: 2^%f", ciphertext2.Level(), params.LogQLvl(ciphertext2.Level()), math.Log2(ciphertext2.Scale.Float64()))
		//-----
		// Step 3: Extend the basis from q to Q
		if err := eval.ApplyEvaluationKey(ciphertext2, eval.EvkDenseToSparse, ciphertext2); err != nil {
			panic(err)
		}
		// printDebug(params, ciphertext2, valuesTest, decryptorSparse, encoder)
		// decryptor2 := rlwe.NewDecryptor(params, )
		// Show decrypted result
		// fmt.Println("\nAfter Sparse Encapsulation: ")
		// printDebug(params, ciphertext2, valuesTest, decryptor, encoder)
		// Show Lvl., LogQ, Scale factor for debugging.
		// fmt.Printf("\n3-1) Level: %d (logQ = %d), Scale: 2^%f", ciphertext2.Level(), params.LogQLvl(ciphertext2.Level()), math.Log2(ciphertext2.Scale.Float64()))
		// Save ciphertext after Sparse Encapsulation
		// fmt.Print("IsNTT:", ciphertext2.IsNTT)
		ciphertext3 := ciphertext2
		ringQ := params.RingQ().AtLevel(0)
		ringQ.INTT(ciphertext2.Value[0], ciphertext3.Value[0])
		ringQ.INTT(ciphertext2.Value[1], ciphertext3.Value[1])
		_, err = fmt.Fprintln(w, "Ciphertext", i, ": ", ciphertext3.Element)
		if err != nil {
			panic(err)
		}
		ringQ.NTT(ciphertext3.Value[0], ciphertext2.Value[0])
		ringQ.NTT(ciphertext3.Value[1], ciphertext2.Value[1])
		if ciphertext2, err = eval.ModUpCustom(ciphertext2); err != nil {
			panic(err)
		}

		// Show the decryption result of ModUp(S2C(ciphertext)), which will not give meaningful values
		// Maybe try appoximately valuesWant:
		// fmt.Println("\nAfter ModRaise: ")
		// printDebug(params, ciphertext2, valuesTest, decryptor, encoder)
		// Show Lvl., LogQ, Scale factor for debugging.
		// fmt.Printf("\n3-2) Level: %d (logQ = %d), Scale: 2^%f", ciphertext2.Level(), params.LogQLvl(ciphertext2.Level()), math.Log2(ciphertext2.Scale.Float64()))

		//-----
		// Step 4: CoeffsToSlots (Homomorphic encoding)
		var real, imag *rlwe.Ciphertext
		if real, imag, err = eval.CoeffsToSlots(ciphertext2); err != nil {
			panic(err)
		}
		// fmt.Println("\nAfter C2S: ")
		// printDebug(params, ciphertext2, valuesTest, decryptor, encoder)

		// Show Lvl., LogQ, Scale factor for debugging.
		// fmt.Printf("\n4) Level: %d (logQ = %d), Scale: 2^%f", ciphertext2.Level(), params.LogQLvl(ciphertext2.Level()), math.Log2(ciphertext2.Scale.Float64()))

		//-----
		// Step 5: EvalMod (Homomorphic modular reduction)
		if real, err = eval.EvalMod(real); err != nil {
			panic(err)
		}

		if imag, err = eval.EvalMod(imag); err != nil {
			panic(err)
		}

		// Recombines the real and imaginary part
		if err = eval.Evaluator.Mul(imag, 1i, imag); err != nil {
			panic(err)
		}
		if err = eval.Evaluator.Add(real, imag, ciphertext2); err != nil {
			panic(err)
		}
		// Show Lvl., LogQ, Scale factor for debugging.
		// fmt.Printf("\n5) Level: %d (logQ = %d), Scale: 2^%f", ciphertext2.Level(), params.LogQLvl(ciphertext2.Level()), math.Log2(ciphertext2.Scale.Float64()))

		fmt.Println("Done")

		//==================
		//=== 5) DECRYPT ===
		//==================

		// Decrypt, print and compare with the plaintext values
		// fmt.Println()
		fmt.Println("Precision of ciphertext vs. Bootstrap(ciphertext)")
		printDebug(params, ciphertext2, valuesTest, decryptor, encoder)
	}

	// // ============ //
	// // For msg = 1  //
	// // ============ //
	w.Flush()

	elapsed2 := time.Since(start2)
	fmt.Printf("******\n%d bootstrappings took %s\n******\n", NumIter, elapsed2)
}

func printDebug(params hefloat.Parameters, ciphertext *rlwe.Ciphertext, valuesWant []complex128, decryptor *rlwe.Decryptor, encoder *hefloat.Encoder) (valuesTest []complex128) {

	slots := ciphertext.Slots()

	if !ciphertext.IsBatched {
		slots *= 2
	}

	valuesTest = make([]complex128, slots)
	// valuesTestNormal := make([]float64, slots)

	if err := encoder.Decode(decryptor.DecryptNew(ciphertext), valuesTest); err != nil {
		panic(err)
	}
	// for i := range valuesTest {
	// 	valuesTestNormal[i] = real(valuesTest[i]) / (36028797019488257.0 / ciphertext.Scale.Float64())
	// }

	// fmt.Println()
	fmt.Printf("Level: %d (logQ = %d)\n", ciphertext.Level(), params.LogQLvl(ciphertext.Level()))
	// params.Q()
	fmt.Printf("Scale: 2^%f\n", math.Log2(ciphertext.Scale.Float64()))
	// fmt.Printf("Normalized decrypted values: ")
	// for i := range valuesTestNormal {
	// 	// for i := 0; i <= 100; i++ {
	// 	if math.Abs(valuesTestNormal[i]) > 1-0.001 {
	// 		fmt.Println(i, ":", valuesTestNormal[i])
	// 	}
	// }
	// fmt.Printf("ValuesTest: %10.14f %10.14f %10.14f %10.14f...\n", valuesTestNormal[0], valuesTestNormal[1], valuesTestNormal[2], valuesTestNormal[3])
	// fmt.Printf("ValuesWant: %10.14f %10.14f %10.14f %10.14f...\n", valuesWant[0], valuesWant[1], valuesWant[2], valuesWant[3])

	precStats := hefloat.GetPrecisionStats(params, encoder, nil, valuesWant, valuesTest, 0, false)

	fmt.Println(precStats.String())
	// fmt.Println()

	return
}
