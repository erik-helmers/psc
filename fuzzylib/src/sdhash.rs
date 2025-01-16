use bytemuck::cast_slice;
use bytemuck::cast_slice_mut;
use sha1::{Digest, Sha1};

use crate::shannon::Shannon;
use crate::tools::Slicetools;
use crate::FuzzyHash;
use crate::Hash;
use crate::bloom;
use crate::RollingHash;


#[derive(Default, Copy, Clone, Debug)]
struct SHA1;
impl<const N: usize> Hash<[u8], [u32; N]> for SHA1{
    fn hash(&self, data: &[u8]) -> [u32; N] {
        let val = sha1::Sha1::digest(data);
        let mut out = [0; N];
        cast_slice_mut(&mut out).copy_from_slice(&val);
        out
    }
}




struct SDHash {
    window_size: usize
}

impl Default for SDHash {
    fn default() -> Self {
        Self { window_size: 64 }
    }
}

type BloomVec = bloom::BloomVec::<[u8], 5, SHA1>;
type BloomFilter = bloom::BloomFilter::<[u8], 5, SHA1>;

impl Hash<[u8], BloomVec> for SDHash {
    fn hash(&self, data: &[u8]) -> BloomVec {
        let entropy = Shannon::<64>.rolling_hash(data)
            .map(|e| (e * 1000.) as u16)
            .collect::<Vec<_>>();

        let popularity = {
            let mut out = vec![0; data.len()];
            let get_max = |w:&[u16]| w.iter().copied().enumerate().max_by_key(|(_,x)| *x).unwrap();
            let (mut imax, mut vmax) : (usize, u16) = get_max(&entropy[0..self.window_size]);
            for (i,w) in entropy.windows(self.window_size).enumerate().skip(1) {
                let new = *w.last().unwrap();
                if new > vmax { imax = i; vmax = new }
                else if i > imax  {
                    (imax, vmax) = get_max(&w);
                    imax += i;
                }
                out[imax] += 1;
            }
            out
        };


        let features = data.chunk_by_indexed(
            |(i,_), _| 100 < popularity[i] && popularity[i] < 990);
        features.into_iter().collect::<BloomVec>()
    }
}

impl FuzzyHash<[u8], BloomVec> for SDHash {
    fn distance(&self, a: &BloomVec, b: &BloomVec) -> f64 {
        if b.len() < a.len() { return self.distance(b, a); }

        fn filter_distance(f: &BloomFilter, g: &BloomFilter) -> f64 {
            //TODO: understand what the paper is describing
            todo!();
        }
        todo!()
    }
}



#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic() {
        println!("{:#x?}", SDHash::default().hash(crate::tests::LONG_STRING_1));
    }
}
