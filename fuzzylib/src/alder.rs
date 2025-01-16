//! This not actually Alder32, but a variant of it that is used in spamsum/ssdeep.
//!
//! It is described in figure 2. of the paper.
//!
//!  Jesse Kornblum. 2006. Identifying almost identical files using context triggered piecewise hashing.
//!  Digital Investigation 3, Supplement (2006)

use crate::{tools::Slicetools, Hash, RollingHash};
use std::num::Wrapping as W;

/// Alder32 rolling hash
///
/// See the module documentation for more information.
pub struct Alder {
    window_size: usize,
}

impl Alder {
    pub fn new(window_size : usize) -> Self {
        Self { window_size }
    }
}

impl  Default for Alder {
    fn default() -> Self {
        Self { window_size: 7 }
    }
}

impl Hash<[u32], u32> for Alder {
    fn hash(&self, data: &[u32]) -> u32 {
        assert_eq!(data.len(), self.window_size);
        self.rolling_hash(data).next().unwrap()
    }
}

impl RollingHash<[u32], u32> for Alder {
    fn rolling_hash<'a>(&'a self, data: &'a [u32]) -> impl Iterator<Item = u32> + 'a {
        data.rolling_windows(self.window_size).scan(
            (W(0u32), W(0u32), W(0u32)),
            move |state, (old, new)| {
                let (mut x, mut y, mut z) = state;
                let (old, new) = (W(old.copied().unwrap_or(0)), W(*new));
                let ws = W(self.window_size as _);
                y = y - x;
                y = y + ws * new;
                x = x + new;
                x = x - old;
                z = z << 5;
                z = z ^ new;

                *state = (x,y,z);

                Some((x + y + z).0)
            },
        )
    }
}
