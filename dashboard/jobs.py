#!/usr/bin/env python3

import os; from os import path
from zipfile import ZipFile
from django.conf import settings
from .models import Sample, Hash


import hashlib


def scan_root():

    root = settings.SAMPLE_ROOT

    if not path.isdir(root):
        raise ValueError(f"The path {root} is not a valid directory.")

    file_list = set(f for f in os.listdir(root) if path.isfile(path.join(root, f)))
    ignore = set(Sample.objects.only('path'))

    samples = (Sample(sid=f, name=f, path=f, signature='unknown') for f in file_list - ignore)

    Sample.objects.bulk_create(samples)





def hash_samples(algo, samples):
    """ Filter out samples that already have a hash with the given algo"""

    exclude = set(Hash.objects.filter(algo=algo, sample__in=samples).values_list('sample_id', flat=True))
    samples = [sample for sample in samples if sample.id not in exclude]

    print(f"Ignored {len(exclude)} samples with existing {algo.sid} hash.")


    if algo.path.startswith('internal:'):
        execute_internal(algo, samples)
    else: execute_external(algo, samples)

def execute_internal(algo, samples):

    hash =  getattr(hashlib, algo.path.split(':')[1])

    root = settings.SAMPLE_ROOT
    hashes = []

    for sample in samples:

        sample_path = path.join(root, sample.path)

        if not path.isfile(sample_path):
            raise ValueError(f"The path {sample_path} is not a valid file.")
        with open(sample_path, 'rb') as f: content = f.read()

        value = hash(content).hexdigest()
        hashes.append(Hash(algo=algo, sample=sample, value=value))


    Hash.objects.bulk_create(hashes)

def execute_external(algo, samples):

    import subprocess as sp

    # Launching a single external hashing process (at algo.path)
    # piping in the samples pathes and reading the output
    # to get the hashes

    sample_root = settings.SAMPLE_ROOT
    algo_root = settings.ALGO_ROOT

    samples_path = '\n'.join(path.join(sample_root, sample.path) for sample in samples) + '\n'
    process = sp.Popen([path.join(algo_root, algo.path)], text=True, stdin=sp.PIPE, stdout=sp.PIPE)

    process.stdin.write(samples_path)
    process.stdin.close()

    count = 0

    while (hashes := process.stdout.readlines(8096)):
        count += len(hashes)
        hashes = [Hash(algo=algo, sample=sample, value=value.strip()) for sample, value in zip(samples[count:], hashes)]
        Hash.objects.bulk_create(hashes)

    process.poll()

    if process.returncode != 0:
        raise ValueError(f"{algo.path} returned with code {process.returncode}.")

    if count != len(samples):
        raise ValueError(f"{algo.path} did not return as many hashes as expected (expected {len(samples)} got {count}).")
