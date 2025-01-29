use crate::{FuzzyHash, Hash};


pub struct Levenshtein;


impl Hash<[u8], Vec<u8>> for Levenshtein {

    fn hash(&self, input: &[u8]) -> Vec<u8> {
        input.into()
    }
}


impl FuzzyHash<[u8], Vec<u8>> for Levenshtein {
    fn distance(&self, a: &Vec<u8>, b: &Vec<u8>) -> f64 {
        triple_accel::levenshtein(a,b) as _
    }
}
