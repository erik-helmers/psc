use std::ops::Index;


pub fn base64(val: usize) -> char{
    let base64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".chars().collect::<Vec<char>>();
    base64[val]
}


pub trait Slicetools<T> {
    /// A bit like `.windows` but the closure only takes optional entering
    /// and leaving elements from the window. This means you can easily
    /// control whether you want to compute on "incomplete" windows.
    fn rolling_windows<'a>(
        &'a self,
        window_size: usize,
    ) -> impl Iterator<Item = (Option<&'a T>, Option<&'a T>)> + 'a where T: 'a;

    /// Like `chunk_by` but with indexes
    fn chunk_by_indexed<'a, F>(&'a self, f: F) -> impl Iterator<Item=&[T]>
    where F: FnMut((usize, &T), (usize, &T)) -> bool + 'a, T: 'a;
}


impl<T> Slicetools<T> for [T] {
    fn rolling_windows<'a>(
        &'a self,
        window_size: usize,
    ) -> impl Iterator<Item = (Option<&'a T>, Option<&'a T>)> + 'a where T:'a
    {
        self.iter().enumerate().map(move |(idx, new)| {
            let old = idx.checked_sub(window_size).map(|old| &self[old]);
            (old, Some(new))
        }).chain(self[self.len()-window_size..].iter().map(|old| (Some(old), None)))
    }

    fn chunk_by_indexed<'a, F>(&'a self, mut f: F) -> impl Iterator<Item=&[T]>
    where F: FnMut((usize, &T), (usize, &T)) -> bool + 'a {
        // SAFETY: this is always safe because we are working on a big slice
        self.chunk_by(move |a, b| { unsafe {
            let i  = (a as *const T).offset_from(&self[0]) as usize;
            let j  = (b as *const T).offset_from(&self[0]) as usize;
            f((i,a),(j,b))
        }})
    }
}




pub trait Counts : Iterator {
    type Result;
    fn counts(self) -> Self::Result;
}


impl<T: Iterator<Item = u8>> Counts for T{
    type Result = [usize; 256];
    fn counts(self) -> Self::Result {
        let mut counts = [0; 256];
        for byte in self {
            counts[byte as usize] += 1;
        }
        counts
    }
}





#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rolling_window_basic() {
        let data = vec![0,1,2,3,4,5,6];
        assert_eq!(data.rolling_windows(2).collect::<Vec<_>>(),
                   vec![(None, Some(&0)), (None, Some(&1)), (Some(&0), Some(&2)), (Some(&1), Some(&3)), (Some(&2), Some(&4)), (Some(&3), Some(&5)), (Some(&4), Some(&6)), (Some(&5), None), (Some(&6), None)])
    }
}
