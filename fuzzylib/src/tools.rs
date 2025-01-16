use std::ops::Index;


pub fn base64(val: usize) -> char{
    let base64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".chars().collect::<Vec<char>>();
    base64[val]
}


pub trait Slicetools<T> {
    fn rolling_windows<'a>(
        &'a self,
        window_size: usize,
    ) -> impl Iterator<Item = (Option<&'a T>, &'a T)> + 'a where T: 'a;


}


impl<T> Slicetools<T> for [T] {
    fn rolling_windows<'a>(
        &'a self,
        window_size: usize,
    ) -> impl Iterator<Item = (Option<&'a T>, &'a T)> + 'a where T:'a
    {
        self.iter().enumerate().map(move |(idx, new)| {
            let old = idx.checked_sub(window_size).map(|old| &self[old]);
            (old, new)
        })
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
                   vec![(None, &0), (None, &1), (Some(&0), &2), (Some(&1), &3), (Some(&2), &4), (Some(&3), &5), (Some(&4), &6)])


    }
}
