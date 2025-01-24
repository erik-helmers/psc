use crate::{Hash, FuzzyHash};
use bytemuck::cast_slice;
use lzjd::{crc32::CRC32BuildHasher, LZDict};


pub struct Lzjd;


impl Hash<[u8], Vec<u8>> for Lzjd {

    fn hash(&self, input: &[u8]) -> Vec<u8> {
        let build_hasher = CRC32BuildHasher;
        let dict = LZDict::from_bytes_stream_lz78(input.iter().copied(), &build_hasher);
        cast_slice(&*dict).to_vec()
    }
}


impl FuzzyHash<[u8], Vec<u8>> for Lzjd {
    fn distance(&self, a: &Vec<u8>, b: &Vec<u8>) -> f64 {
        let l1 : LZDict = cast_slice(a).to_vec().into();
        let l2 : LZDict = cast_slice(b).to_vec().into();
        return l1.dist(&l2);
    }
}
