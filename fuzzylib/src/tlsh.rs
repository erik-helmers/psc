use crate::{pearson::Pearson, tools::Counts, FuzzyHash, Hash};

#[derive(Default, Clone, Copy)]
struct Tlsh;

// TODO: Implement the headers q_ratio
#[derive(Debug)]
struct Digest {
    hist: [u8; 256],
}

fn triplets(w: &[u8]) -> [[u8; 3]; 6] {
    [
        [w[0], w[1], w[2]],
        [w[0], w[1], w[3]],
        [w[0], w[1], w[4]],
        [w[0], w[2], w[3]],
        [w[0], w[2], w[4]],
        [w[0], w[3], w[4]],
    ]
}

impl Hash<[u8], Digest> for Tlsh {
    fn hash(&self, data: &[u8]) -> Digest {

        let counts = data
            .windows(5)
            .flat_map(|w| triplets(w).into_iter().map(|t| Pearson::default().hash(&t)))
            .counts();

        let (q1, q2, q3) = {
            let sorted = { let mut x = counts.clone(); x.sort(); x };
            let q1 = sorted[sorted.len() / 4];
            let q2 = sorted[sorted.len() / 2];
            let q3 = sorted[sorted.len() * 3 / 4];
            (q1, q2, q3)
        };

        let hist = counts.into_iter().map(|c| {
            if c < q2 {if c < q1 {1} else {2}}
            else {if c < q3 {3} else {4}}
        }).collect::<Vec<u8>>();

        Digest { hist: hist.try_into().unwrap() }


    }
}

impl FuzzyHash<[u8], Digest> for Tlsh {
    fn distance(&self, a: &Digest, b: &Digest) -> f64 {
        // TODO: explore some other distances (this is one is arbitrary i feel like)
        //  - Bhattacharyya distance
        //  - Hellinger distance
        //  https://crucialbits.com/blog/a-comprehensive-list-of-similarity-search-algorithms/
        a.hist.iter().zip(b.hist.iter()).fold(0, |acc, (&x, &y)| {
            if (x==0 && y==3) || (x==3 && y==0) {acc + 6}
            else if x != y {acc + 1}
            else {acc}
        }) as _
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tlsh_basic() {
        let tlsh = Tlsh::default();
        let h1 = tlsh.hash(b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa1");
        let h2 = tlsh.hash(b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa2");
        let h3 = tlsh.hash(b"aaa2aaaaaa2aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa2aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
        let h4 = tlsh.hash(b"mlakfjmleakj ffljeamlfkj amlkjflm soiufpoisqljcwvlmealfkjamlfekjamlfkjeamlkfjeamlkjfamlkjamlkfjljflkjfnvw;nvmljmfqlhfpoqziuhflkjwlvjxmljdsqmfoqhfqkjsblkjvbcxwlkjvclkhjfeaxlfejamljeamlfkjeamlfkjamlkfml");
        assert_eq!(tlsh.distance(&h1, &h1), 0.0);
        assert_eq!(tlsh.distance(&h1, &h2), 0.0);
        assert!(tlsh.distance(&h2, &h3) < 10.0);
        assert!(tlsh.distance(&h3, &h4) > 300.0);
    }
}
