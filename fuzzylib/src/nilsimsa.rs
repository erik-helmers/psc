use bitvec::{array::BitArray, order::Lsb0, view::BitView as _};

use crate::{pearson::Pearson, tools::Counts, FuzzyHash, Hash};


#[derive(Default, Copy, Clone)]
pub struct Nilsimsa;

fn essential_triplets(w: &[u8]) -> [[u8;3]; 6] {
        [[w[0],w[1],w[2]],
        [w[0],w[1],w[3]],
        [w[0],w[1],w[4]],
        [w[0],w[2],w[3]],
        [w[0],w[2],w[4]],
        [w[0],w[3],w[4]]]
}

impl Hash<[u8], [u8;32]> for Nilsimsa {
    fn hash(&self, data: &[u8]) -> [u8; 32] {
        let window_size = 5;

        let hist = data.windows(window_size)
            .flat_map(|w|{essential_triplets(w).map(|t| Pearson.hash(&t))})
            .counts();

        let mut out = BitArray::<[u8;32]>::default();
        let mean = hist.iter().sum::<usize>() as f64 / 256.;
        hist.iter().enumerate().for_each(
            |(idx,&count)| out.set(idx, count as f64 >= mean));
        out.data
    }
}

impl FuzzyHash<[u8], [u8;32]> for Nilsimsa {
    fn distance(&self, a: &[u8;32], b: &[u8;32]) -> f64 {
        // This is hamming on bits
        let a = a.view_bits::<Lsb0>();
        let b = b.view_bits::<Lsb0>();
        a.iter().zip(b.iter())
            .filter(|(x,y)| x!=y)
            .count() as f64
    }
}



#[cfg(test)]
mod test {

    use super::*;

    fn distance(l1: &[u8], l2: &[u8]) -> f64 {
        let nilsimsa = Nilsimsa ;
        nilsimsa.distance(
            &nilsimsa.hash(l1),
            &nilsimsa.hash(l2),
        )
    }

    #[test]
    fn basic_test() {
        let left =  b"hallo world 0123456789 abcdefghi 0123456789 abcdefghi";
        let right = b"hallo world 0123456789 abcdefghi 0123456789 abcdefghi";
        let distance = distance(left, right);
        assert!(distance < 10., "dist: {distance} too big");
    }

}
