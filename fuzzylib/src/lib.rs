pub mod tools;
pub mod features;
#[cfg(test)]
pub mod tests;

pub mod alder;
pub mod fnv;
pub mod ssdeep;


pub mod bloom;
pub mod shannon;
pub mod sdhash;

pub mod nilsimsa;

pub mod pearson;
pub mod tlsh;

pub mod lzjd;


pub trait Hash<Data: ?Sized, Digest> {
    fn hash(&self, data: &Data) -> Digest;
}

pub trait RollingHash<Data: ?Sized, Digest> : Hash<Data, Digest> {
    fn rolling_hash<'a>(&'a self, data: &'a Data) -> impl Iterator<Item=Digest> + 'a;
}

pub trait FuzzyHash<Data: ?Sized, Digest> : Hash<Data, Digest>{
    fn distance(&self, a: &Digest, b: &Digest) -> f64;
}

