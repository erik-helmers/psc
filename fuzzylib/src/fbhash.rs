use rand::{thread_rng, Rng};
use rand::distributions::Alphanumeric;
use std::collections::{HashMap, HashSet};
use std::f64;
use std::iter;

fn rand_str(n: usize) -> String {
    thread_rng()
        .sample_iter(&Alphanumeric)
        .take(n)
        .map(char::from)
        .collect()
}

fn chunk_calc(data: &str, k: usize) -> Vec<&str> {
    data.chars()
        .collect::<Vec<char>>()
        .windows(k)
        .map(|chunk| chunk.iter().collect::<String>())
        .collect::<Vec<_>>()
        .iter()
        .map(|s| s.as_str())
        .collect()
}

fn roll_hash(chunks: &[&str]) -> Vec<u64> {
    let a: u64 = 255;
    let n: u64 = 801385653117583579;
    let mut hashes = Vec::new();

    for &chunk in chunks {
        let mut h: u64 = 0;
        let mut k = chunk.len() as u32;
        for c in chunk.chars() {
            h += (c as u64) * a.pow(k - 1);
            k -= 1;
        }
        hashes.push(h % n);
    }

    hashes
}

fn chunk_freq(hashes: &[u64]) -> HashMap<u64, usize> {
    let mut freq_map = HashMap::new();
    for &hash in hashes {
        *freq_map.entry(hash).or_insert(0) += 1;
    }
    freq_map
}

fn chunk_weight(freq_map: &HashMap<u64, usize>) -> HashMap<u64, f64> {
    freq_map
        .iter()
        .map(|(&hash, &freq)| (hash, 1.0 + (freq as f64).log10()))
        .collect()
}

fn doc_freq(hashes: &[u64], dataset: &[String]) -> HashMap<u64, usize> {
    let mut freq_map = HashMap::new();

    for doc in dataset {
        let chunks = chunk_calc(doc, 7);
        let doc_hashes: HashSet<u64> = roll_hash(&chunks).into_iter().collect();

        for &hash in doc_hashes.iter() {
            *freq_map.entry(hash).or_insert(0) += 1;
        }
    }

    freq_map
}

fn doc_weight(freq_map: &HashMap<u64, usize>, total_docs: usize) -> HashMap<u64, f64> {
    freq_map
        .iter()
        .map(|(&hash, &freq)| {
            if freq > 0 {
                (hash, ((total_docs as f64 / freq as f64).powi(2)).log10())
            } else {
                (hash, 1.0)
            }
        })
        .collect()
}

fn chunk_score(weight_map: &HashMap<u64, f64>, doc_weights: &HashMap<u64, f64>) -> Vec<f64> {
    weight_map
        .iter()
        .filter_map(|(&hash, &chunk_weight)| {
            doc_weights.get(&hash).map(|&doc_weight| chunk_weight * doc_weight)
        })
        .collect()
}

fn similarity_score(d1: &[f64], d2: &[f64]) -> f64 {
    let numerator: f64 = d1.iter().zip(d2.iter()).map(|(x, y)| x * y).sum();
    let denom1: f64 = d1.iter().map(|x| x.powi(2)).sum::<f64>().sqrt();
    let denom2: f64 = d2.iter().map(|x| x.powi(2)).sum::<f64>().sqrt();

    (numerator / (denom1 * denom2)) * 100.0
}

fn fb_hash(document: &str, dataset: &[String]) -> Vec<f64> {
    let chunks = chunk_calc(document, 7);
    let hashes = roll_hash(&chunks);
    let freq_map = chunk_freq(&hashes);
    let weight_map = chunk_weight(&freq_map);
    let doc_freq_map = doc_freq(&hashes, dataset);
    let doc_weight_map = doc_weight(&doc_freq_map, dataset.len());
    chunk_score(&weight_map, &doc_weight_map)
}

fn main() {
    let dataset: Vec<String> = iter::repeat_with(|| rand_str(52))
        .take(1000)
        .chain(vec![
            "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm".to_string(),
            "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM".to_string(),
        ])
        .collect();

    let d1 = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm";
    let d2 = d1;

    let digest1 = fb_hash(d1, &dataset);
    let digest2 = fb_hash(d2, &dataset);

    let score = similarity_score(&digest1, &digest2);
    println!("Similarity score of D1 and D2: {:.5}%", score);
}
