use crate::Hash;

/// This is the FNV-1 hash that is used in the ssdeep paper.
///
/// It is the 32 bit variant of the hash. Described at :
/// https://en.wikipedia.org/wiki/Fowler%E2%80%93Noll%E2%80%93Vo_hash_function
pub struct Fnv;
impl Default for Fnv {
    fn default() -> Self {
        Self::new()
    }
}

impl Fnv {
    pub fn new() -> Self {
        Fnv
    }
}

impl Hash<[u32], u32> for Fnv {

    fn hash(&self, data: &[u32]) -> u32 {
        const PRIME: u32 = 0x01000193;
        const OFFSET: u32 = 0x811c9dc5;
        data.iter().fold(OFFSET, |hash, byte| (hash.wrapping_mul(PRIME)) ^ byte)
    }
}


