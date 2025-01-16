use bytemuck::cast_slice;
use fuzzy_hash::nilsimsa::Nilsimsa;
use pyo3::prelude::*;
use pyo3::types::PyIterator;
use rayon::iter::{IntoParallelIterator, ParallelIterator};

use std::collections::{HashMap, HashSet};
use std::{fs, io};

use fuzzy_hash::{FuzzyHash, Hash};



// fn hash<H: PyFuzzyHash>(hash: &H, bytes: &[u8]) -> PyResult<Box<[u8]>> {
//     Ok(hash.hash(bytes))
// }

// fn distance<H: PyFuzzyHash>(hash: &H, left: Box<[u8]>, right: Box<[u8]> ) -> PyResult<f64> {
//     Ok(hash.distance(&left, &right))
// }
//
trait PyFuzzyHash<Digest: Send + Sync> : Send + Sync {
    fn hash(&self, data: &[u8]) -> Digest;
    fn distance(&self, a: &Digest, b: &Digest) -> f64;

    fn batch_hash(&self, pairs: Bound<'_, PyIterator>) -> PyResult<Vec<(String, String, f64)>> {

        let pairs : Vec<_> = pairs
            .try_iter()?
            .map(|res| res?.extract::<(String, String)>())
            .collect::<Result<_, _>>()?;

        let filenames : HashSet<_> = pairs.iter()
            .flat_map(|(a,b)| vec![a.clone(), b.clone()])
            .collect();

        let hashes : HashMap<_, _> = filenames.into_par_iter()
            .map(|f| Ok::<_, io::Error>((f.clone(), self.hash(&fs::read(f)?) )) )
            .collect::<Result<_, _>>()?;

        let distances = pairs.into_par_iter()
            .map(|(a,b)|{
                let d = self.distance(&hashes[&a], &hashes[&b]);
                (a, b, d)
            })
            .collect();

        Ok(distances)
    }
}


impl<T, Digest: Send + Sync> PyFuzzyHash<Digest> for T where T: FuzzyHash<[u8], Digest> + Send + Sync {
    fn hash(&self, data: &[u8]) -> Digest {
        T::hash(self, data)
    }

    fn distance(&self, a: &Digest, b: &Digest) -> f64 {
        T::distance(self, a, b)
    }
}








#[pymodule]
pub mod fuzzylib {

    // This doesn't work if we ue the macros directly in here, don't know why
    #[pymodule_export]
    use super::py::nilsimsa;
    #[pymodule_export]
    use super::py::ssdeep;
    #[pymodule_export]
    use super::py::tlsh;
}



mod py {
    use super::*;
    /// This macro generates the Python function binding for a FuzzyHash implementation
    macro_rules!  fuzzy_hash {
        ($name:ident, $hash:path) => {
            #[pymodule]
            pub mod $name {
                use super::*;

                #[pyfunction]
                pub fn batch_hash(pairs: Bound<'_, PyIterator>) -> PyResult<Vec<(String, String, f64)>> {
                    $hash.batch_hash(pairs)
                }

            }
        };
    }

    fuzzy_hash!(ssdeep, fuzzy_hash::ssdeep::SSDeep::default());
    fuzzy_hash!(nilsimsa, fuzzy_hash::nilsimsa::Nilsimsa);
    fuzzy_hash!(tlsh, fuzzy_hash::tlsh::Tlsh);
    // fuzzy_hash!(sdhash, fuzzy_hash::sdhash::SDHash::default());
    // fuzzy_hash!(sise, fuzzy_hash::sise::Sise::default());

}
