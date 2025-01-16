use std::marker::PhantomData;

use crate::Hash;
use bitvec::prelude::*;

#[derive(Debug)]
/// Represent a bloom filter taking some `&T`, computing
/// `N` hashes using the hash `H`;
pub struct BloomFilter<T, const N: usize, H>
where
    T: ?Sized,
    H: Hash<T, [u32; N]>,
{
    pub content: BitVec,
    count: usize,
    hasher: H,
    _phantom: PhantomData<T>,
}

impl<T, const N: usize, H> Default for BloomFilter<T, N, H>
where
    T: ?Sized,
    H: Hash<T, [u32; N]> + Default,
{
    fn default() -> Self {
        Self::new(256 * 8, H::default())
    }
}

impl<T, const N: usize, H> BloomFilter<T, N, H>
where
    T: ?Sized,
    H: Hash<T, [u32; N]>,
{
    pub fn new(size: usize, hasher: H) -> Self {
        Self {
            content: bitvec![0; size],
            count: 0,
            hasher,
            _phantom: PhantomData,
        }
    }

    pub fn query(&self, item: &T) -> bool {
        let len = self.content.len();
        self.hasher.hash(item).iter()
            .all(|h| self.content[*h as usize % len])
    }

    pub fn insert(&mut self, item: &T) {
        let len = self.content.len();
        let hash = self.hasher.hash(item);
        hash.iter().for_each(|h| self.content.set(*h as usize % len, true));
    }
}

#[derive(Debug)]
pub struct BloomVec<T, const N: usize, H>
where
    T: ?Sized,
    H: Hash<T, [u32; N]> + Clone,
{
    filter_size: usize,
    max_filter_count: usize,
    filters: Vec<BloomFilter<T, N, H>>,
    hasher: H,
}
impl<T, const N: usize, H> Default for BloomVec<T, N, H>
where
    T: ?Sized,
    H: Hash<T, [u32; N]> + Default + Clone {
        fn default() -> Self {
            Self::new(256*8, 128, Default::default())
    }
}


impl<T, const N: usize, H> BloomVec<T, N, H>
where
    T: ?Sized,
    H: Hash<T, [u32; N]> + Clone
{
    pub fn new(filter_size: usize, max_filter_count: usize, hasher: H) -> Self {
        Self {
            filter_size,
            max_filter_count,
            filters: vec![BloomFilter::new(filter_size, hasher.clone())],
            hasher,
        }
    }
    pub fn len(&self) -> usize {
        self.filters.len()
    }

    fn add_filter(&mut self) -> &mut BloomFilter<T, N, H> {
        let filter = BloomFilter::new(self.filter_size, self.hasher.clone());
        self.filters.push(filter);
        self.filters.last_mut().unwrap()
    }

    pub fn insert(&mut self, item: &T) {
        let last = self.filters.last_mut().unwrap();
        if last.query(item) {return;}
        let last =
            if last.count < self.max_filter_count {last}
            else {self.add_filter()};
        last.insert(item)
    }

}


impl<'a, T, const N: usize, H> FromIterator<&'a T> for BloomVec<T, N, H>
where
    T: ?Sized,
    H: Hash<T, [u32; N]> + Clone + Default
{
    fn from_iter<Iter: IntoIterator<Item=&'a T>>(iter: Iter) -> Self {
        let mut out = BloomVec::default();
        iter.into_iter().for_each(|item| out.insert(item));
        out
    }
}
