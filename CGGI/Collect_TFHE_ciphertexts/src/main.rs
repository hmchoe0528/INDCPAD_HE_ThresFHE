use tfhe::boolean::prelude::*;
use rayon::prelude::*;
use std::time::Instant;

// Our modified parameters
pub const CUSTOM_PARAMS_128BITS_SECURE: BooleanParameters = BooleanParameters {
    lwe_dimension: LweDimension(600),
    glwe_dimension: GlweDimension(7),
    polynomial_size: PolynomialSize(128),
    lwe_modular_std_dev: StandardDev(11.0*0.000013071021089943935),
    glwe_modular_std_dev: StandardDev(11.0*0.00000004990272175010415),
    pbs_base_log: DecompositionBaseLog(6),
    pbs_level: DecompositionLevelCount(3),
    ks_base_log: DecompositionBaseLog(3),
    ks_level: DecompositionLevelCount(4),
    encryption_key_choice: EncryptionKeyChoice::Small,
};

fn main() {    
    // We generate a set of client/server keys
    let client_key = ClientKey::new(&CUSTOM_PARAMS_128BITS_SECURE);
    let server_key = ServerKey::new(&client_key);

    // The total number of samples is \gamma = NB_ITER * ARRAY_SIZE
    const NB_ITER: usize = 1000*1;
    const ARRAY_SIZE: usize = 1*1000;

    let start = Instant::now();
    let mut nb_failures = 0;
    for i in 0..NB_ITER {
        eprintln!("{} / {}", i, NB_ITER);
        let starti = Instant::now();

        // --- Choice of messages ---
        // Message input is all True
        let arr = [true; ARRAY_SIZE];

        
        // --- Encryption Oracle ---
        let ct_arr: Vec<_> = arr.par_iter().map(|x| client_key.encrypt(*x)).collect();

        // --- Evaluation oracle ---
        // Homomorphic evaluations
        // Obtaining ciphertexts with error after bootstrapping
        let ct_bts: Vec<_> = ct_arr.par_iter().map(|x| server_key.and(x, x)).collect();

        // Apply Gate AND on the same ciphertext
        let ct_out: Vec<_> = ct_bts.par_iter().map(|x| server_key.and(x, x)).collect();

        // --- Decryption oracle ---
        let res: Vec<_> = ct_out.par_iter().map(|x| client_key.decrypt(x)).collect();
        
        // Outputting ciphertext coefficients of failed ciphertexts
        for r in 0..ARRAY_SIZE {
            if res[r] == false {
                nb_failures += 1;
                let ct = &ct_bts[r];
                match ct {
                    Ciphertext::Trivial(_b) => { println!("triv;");},
                    Ciphertext::Encrypted(lwe_ciphertext) => {
                        let (mask, body) = lwe_ciphertext.get_mask_and_body();
                        println!("Mask {:#?}", mask);
                        println!("body {:#?}", body);
                    }
                }
            }
        }
        let elapsedi = starti.elapsed();
        let elapsed = start.elapsed();
        eprintln!("{} s spent / {} ms ", elapsed.as_secs(), (NB_ITER as u128)*elapsedi.as_millis()); 
    }
    println!("Number of failures = {}", nb_failures);
    // To measure performances of the attack, we output the secret key to compare to the guess
    println!("{:#?}", client_key);
    println!("end");
}