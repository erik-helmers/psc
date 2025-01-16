use crate::{tools::Slicetools, Hash, RollingHash};

/// Shannon entropy calculation
///
/// This of course, is not a hash per se, but it works well enough
/// To consider it is one


#[derive(Debug, Clone, Copy, Default)]
pub struct Shannon<const W: usize = 64> ;


impl<const W: usize> Shannon<W>{
    const WINDOW_SIZE: usize = W;
}

impl Shannon<64> {
    //  facts = [0] + [(-(p:=i/64) * log2(p)) for i in range(1, 65)]
    const TERMS: [f64; Self::WINDOW_SIZE + 1] = [
        0.0000000000000000000000000, 0.0937500000000000000000000, 0.1562500000000000000000000, 0.2069548827786958089536284,
        0.2500000000000000000000000, 0.2873493675869248087373364, 0.3201597655573916179072569, 0.3491955553999495642791828,
        0.3750000000000000000000000, 0.3979792966721748537217707, 0.4184487351738496729858241, 0.4366601905467145106065630,
        0.4528195311147832358145138, 0.4670981822525906435039644, 0.4796411107998990730472144, 0.4905725166542534432245759,
        0.5000000000000000000000000, 0.5080176827928786220667234, 0.5147085933443495964212389, 0.5201465194464355290548951,
        0.5243974703476992349493457, 0.5275208456507193277573720, 0.5295703810934290212131259, 0.5305949220420109746498838,
        0.5306390622295664716290275, 0.5297436758692481983956668, 0.5279463645051812870079289, 0.5252818350247867584812411,
        0.5217822215997981460944288, 0.5174773615828188733090087, 0.5123950333085069974714543, 0.5065611621563573807591752,
        0.5000000000000000000000000, 0.4927342822057974580651774, 0.4847853655857571886222956, 0.4761733501082214825572692,
        0.4669171866886993038647802, 0.4570347729957633942099449, 0.4465430388928710581097903, 0.4354580228808174191534874,
        0.4237949406953985809209939, 0.4115682470415401583707649, 0.3987916913014386000035927, 0.3854783679345279434613758,
        0.3716407621868581534485543, 0.3572907916431974917337300, 0.3424398440840220048109188, 0.3270988120492350215151589,
        0.3112781244591328322357526, 0.2949877755992936778639546, 0.2782373517384963412801824, 0.2610360556164644241228245,
        0.2433927290103626017714333, 0.2253158735648506660886881, 0.2068136700495734336957554, 0.1878939961897456434325449,
        0.1685644431995964032111601, 0.1488323311345269572836258, 0.1287047231656377743735931, 0.1081884388695525806012299,
        0.0872900666170138700428183, 0.0660159751353740220647381, 0.0443723243127146366182600, 0.0223650753047697249675796,
        0.0000000000000000000000000
    ];
}

impl Hash<[u8], f64> for Shannon<64> {

    fn hash(&self, data: &[u8]) -> f64 {
        assert_eq!(data.len(), Self::WINDOW_SIZE);

        let mut counts = [0; 256];
        data.iter().for_each(|b| counts[*b as usize] += 1);
        counts.iter().map(|c| Self::TERMS[*c as usize]).sum()
    }
}

impl RollingHash<[u8], f64> for Shannon<64> {
    fn rolling_hash<'a>(&'a self, data: &'a [u8]) -> impl Iterator<Item=f64> + 'a {
        data.rolling_windows(Self::WINDOW_SIZE)
            .scan((0.0, [0u8;256]), |(entropy, counts), (old, new)| {
                if old == Some(new) {return Some(*entropy);}

                let mut update = |val:u8, delta: i16| {
                    let old_count = counts[val as usize] as usize;
                    let new_count = (old_count as i16 + delta as i16) as usize;
                    counts[val as usize] = new_count as u8;
                    Self::TERMS[new_count] - Self::TERMS[old_count]
                };

                if let Some(&old) = old { *entropy += update(old, -1);}
                *entropy += update(*new, 1);
                Some(*entropy)
            }).skip(Self::WINDOW_SIZE - 1)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn shannon_basic() {
        let shannon = Shannon::<64>::default();
        assert_eq!(shannon.hash(b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"), 0.0);
        assert_eq!(shannon.hash(b"abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijkl"), 4.67095859334435);
        assert_eq!(shannon.hash(b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!-"), 6.0);
    }

    #[test]
    fn shannon_rolling() {
        let shannon = Shannon::<64>::default();
        let data = b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!-";
        let hashes: Vec<_> = shannon.rolling_hash(data).collect();
        assert_eq!(hashes.len(), data.len() - 64 + 1);
        assert_eq!(hashes[0], 0.0);
        assert_eq!(hashes[hashes.len()-1], 6.000000000000001);
    }
}
