//! ssdeep - Jesse Kornblum - 2006
//!
//!
//!  Jesse Kornblum. 2006. Identifying almost identical files using context triggered piecewise hashing.
//!  Digital Investigation 3, Supplement (2006)
//!
//! This paper was also used to clarify some details of the algorithm:
//!
//!  Carlo Jakobs*. 2022. Evaluating and improving ssdeep.
//!  Digital Investigation 42 (2022)

use bytemuck::cast_slice;

use crate::FuzzyHash;
use crate::{alder::Alder, fnv::Fnv, Hash, RollingHash};
use crate::tools::base64;



pub struct SSDeep {
    min_block_size: usize,
    window_size: usize,
    output_size: usize,
}
impl SSDeep {
    pub fn new(min_block_size: usize, window_size: usize, output_size: usize) -> Self {
        Self { min_block_size, window_size, output_size }
    }
}
impl Default for SSDeep {
    fn default() -> Self {
        Self::new(3, 7, 64)
    }
}

pub struct Digest {
    pub sig1: Vec<u32>,
    pub sig2: Vec<u32>,
    pub block_size: usize
}

impl Hash<[u32], Digest> for SSDeep {
    fn hash(&self, data: &[u32]) -> Digest {
        let min_bs = self.min_block_size;
        let triggers = Alder::new(self.window_size).rolling_hash(data).collect::<Vec<_>>();
        let features = |bs: u32| triggers.chunk_by(|_, x| x%bs!=bs-1).collect::<Vec<_>>();

        let mut block_size = {
            let n = data.len();
            let s = self.output_size;
            let factor = n/s * min_bs;
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


impl Hash<[u8], Digest> for SSDeep {
    fn hash(&self, data: &[u8]) -> Digest {
        //HACK: drop the extra bytes so we always get a proper &[u32]
        let data = &data[0..data.len() & !0b11];
        self.hash(cast_slice(data) as &[u32])
    }
}
impl FuzzyHash<[u8], Digest> for SSDeep {
    fn distance(&self, a: &Digest, b: &Digest) -> f64 {
        let dist = triple_accel::levenshtein(
            a.to_string().as_bytes(),
            b.to_string().as_bytes());
        dist as _
    }
}


impl ToString for Digest {
    fn to_string(&self) -> String {
        let sig = |sig: &Vec<_>| sig.iter().map(|v| base64(*v as usize & 0x3F)).collect::<String>();
        format!("{}:{}:{}", self.block_size, sig(&self.sig1), sig(&self.sig2))
    }
}




#[cfg(test)]
mod tests {
    use super::*;

    fn hash(bytes: &[u8]) -> String {
        let data : Vec<u32> = bytes.iter().map(|v| *v as u32).collect();
        let hash =  SSDeep::default().hash(&data as &[u32]);
        hash.to_string()
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

