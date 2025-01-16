//! This module helps defining `features` for an input ie chunks
//! of data that will be processed (typically hashed) then aggregated into the digest.
//!
//! CTPH (Context Triggered Piecewise Hashing) hashes typically has rather large,
//! non-overlapping features, while other classes of algorithms like LSH have many small
//! overlapping features. This module provides ways to construct them.

use std::ops::Index;


#[derive(Debug, Copy, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct  Feature {
    /// The start index of the feature in the original input data
    start: usize,
    /// The end index of the feature in the original input data
    end : usize
}


impl Feature {

    /// Create a new feature
    pub fn new(start: usize, end: usize) -> Feature {
        assert!(start <= end);
        Feature { start, end }
    }

    /// Get the start index of the feature in the original input data
    pub fn start(&self) -> usize {
        self.start
    }

    /// Get the end index (exclusive) of the feature in the original input data
    pub fn end(&self) -> usize {
        self.end
    }

    /// Get the length of the feature in elements of the original input data
    pub fn len(&self) -> usize {
        self.end - self.start
    }

}

impl Feature {

    /// Check if the feature overlaps with another feature
    pub fn overlaps(&self, other: &Feature) -> bool {
        self.start < other.end && self.end > other.start
    }
}

impl<T> Index<Feature> for [T] {
    type Output = [T];

    fn index(&self, index: Feature) -> &Self::Output {
        &self[index.start..index.end]
    }
}




#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PartitionAction {
    /// The elemenet is added to the current feature
    Continue,
    /// The element is the first of a new feature, the current feature is saved
    Save,
    /// The element is the first of a new feature, the current feature is dropped
    Discard,
}


#[derive(Clone)]
pub struct PartitionIterator<'a, T, F>
 where F: FnMut(&T) -> PartitionAction {
    data: &'a [T],
    callback: F,
    start: usize,
}

impl<'a, T, F> PartitionIterator<'a, T, F>
 where F: FnMut(&T) -> PartitionAction {

    pub fn new(data: &'a [T], callback: F) -> Self {
        PartitionIterator { data, start: 0, callback }
    }
}

impl<'a, T, F> Iterator for PartitionIterator<'a, T, F>
 where F: FnMut(&T) -> PartitionAction {

    type Item = Feature;

    fn next(&mut self) -> Option<Self::Item> {
        let mut cur = self.start + 1;
        while cur < self.data.len() {
            match (self.callback)(&self.data[cur]) {
                PartitionAction::Continue => cur += 1,
                PartitionAction::Discard => {self.start = cur; cur += 1},
                PartitionAction::Save => {
                    let out = Feature::new(self.start, cur);
                    self.start = cur;
                    return Some(out);
                },
            }
        }
        if self.start < self.data.len() {
            let out = Feature::new(self.start, self.data.len());
            self.start = self.data.len();
            Some(out)
        } else {
            None
        }
    }

}

/// Partition the input data into features based on a callback
/// The callback is called for each element of the input data and should return
/// `Continue` if the element is part of the current feature, `Save` if the element
/// is the first of a new feature and the current feature should be saved, and `Discard`
/// if the element is the first of a new feature and the current feature should be discarded.
pub fn partition<T, F>(data: &[T], callback: F) -> PartitionIterator<'_, T, F>
 where F: FnMut(&T) -> PartitionAction {
    PartitionIterator::new(data, callback)
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn partition_basic() {
        let data = vec![0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
        let features = partition(&data, |x| {
            if *x == 6 {PartitionAction::Discard}
            else if *x % 2 == 0 {PartitionAction::Save}
            else {PartitionAction::Continue}
        }).collect::<Vec<_>>();
        assert_eq!(
            features,
            vec![Feature { start: 0, end: 2 }, Feature { start: 2, end: 4 },
                 Feature { start: 6, end: 8 }, Feature { start: 8, end: 10 }]);

    }
}
