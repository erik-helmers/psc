pub mod tools;
pub mod features;

pub mod alder;
pub mod fnv;
pub mod ssdeep;


pub mod bloom;
pub mod shannon;
pub mod sdhash;

pub mod nilsimsa;

pub trait Hash<Data: ?Sized, Digest> {
    fn hash(&self, data: &Data) -> Digest;
}

pub trait RollingHash<Data: ?Sized, Digest> : Hash<Data, Digest> {
    fn rolling_hash<'a>(&'a self, data: &'a Data) -> impl Iterator<Item=Digest> + 'a;
}

pub trait FuzzyHash<Data: ?Sized, Digest> : Hash<Data, Digest>{
    fn distance(&self, a: &Digest, b: &Digest) -> f64;
}

#[cfg(test)]
#[allow(dead_code, unused_variables)]
mod tests {
    use super::*;


    struct Roll {}

    impl Hash<[u8], u8> for Roll {
        fn hash(&self, data: &[u8]) -> u8 {
            0
        }
    }

    impl RollingHash<[u8], u8> for Roll {
        fn rolling_hash<'a>(&'a self, data: &'a[u8]) -> impl Iterator<Item=u8> + 'a {
            data.iter().copied()
        }
    }
}
