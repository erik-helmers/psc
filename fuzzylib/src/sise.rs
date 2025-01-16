//! SiSe - Victor Gayoso Martinez et al. - 2020
//!
//! An Improved Bytewise Approximate
//! Matching Algorithm Suitable for Files of Dissimilar Sizes
//!
//! Here, the digest is almost the same as SSDeep but with longer signatures
//!  - more features are selected
//!  - each hashed features contributes more characters

use crate::{alder::Alder, fnv::Fnv, tools::base64, Hash, RollingHash};



pub struct SiSe {
    min_block_size: usize,
    window_size: usize,
    output_size: usize,
}

impl SiSe {
    pub fn new(min_block_size: usize, window_size: usize, output_size: usize) -> Self {
        Self { min_block_size, window_size, output_size }
    }
}
impl Default for SiSe {
    fn default() -> Self {
        Self::new(3, 7, 64)
    }
}

pub struct Digest {
    pub sig1: Vec<u32>,
    pub sig2: Vec<u32>,
    pub block_size: usize
}

impl Hash<[u32], Digest> for SiSe {
    fn hash(&self, data: &[u32]) -> Digest {
        let min_bs = self.min_block_size;
        let triggers = Alder::new(self.window_size).rolling_hash(data).collect::<Vec<_>>();
        let features = |bs: u32| triggers.chunk_by(|_, x| x%bs!=bs-1).collect::<Vec<_>>();

        let mut block_size = {
            let n = data.len();
            let s = self.output_size;
            let factor = n/(s * min_bs);
            min_bs * if factor > 0 { 1 << factor.ilog2() } else { 1 }
        };

        while block_size > min_bs
            && features(block_size as _).len() < self.output_size / 2 {
            block_size /= 2;
        }

        let digest = |feat: Vec<_>| feat.into_iter().map(|feat| Fnv::new().hash(feat)).collect();

        Digest {
            block_size,
            sig1: digest(features(  block_size as u32)),
            sig2: digest(features(2*block_size as u32)),
        }
    }
}

impl Into<String> for Digest {
    fn into(self) -> String {
        let sig = |sig: Vec<_>| sig.iter().map(|v| base64(*v as usize & 0x3F)).collect::<String>();
        format!("{}:{}:{}", self.block_size, sig(self.sig1), sig(self.sig2))
    }
}




#[cfg(test)]
mod tests {
    use super::*;

    fn hash(bytes: &[u8]) -> String {
        let data : Vec<u32> = bytes.iter().map(|v| *v as u32).collect();
        let hash =  SiSe::default().hash(&data);
        hash.into()
    }

    #[test]
    fn basic() {
        let h1 = hash(b"hello world this is me, mario! hello world this is me, mario! hello world this is me, mario! hello world this is me, mario!");
        let h2 = hash(b"hella warld this is me, maria! hello world this is me, mario! hello world this is me, mario! hello world this is me, mario!");
        println!(" h1: {}\n h2: {}", h1, h2);
        let dist = triple_accel::levenshtein(h1.as_bytes(), h2.as_bytes());
        assert!(dist < 20, " h1: {},\n h2: {},\n dist: {}", h1, h2, dist)

    }
}
