#!/usr/bin/env python
# coding: utf-8


import itertools
import time
import numpy as np
import csv
import pandas as pd

import argparse
import subprocess
import tempfile
from pathlib import Path
from Bio import SeqIO

import sys
from Bio import SeqIO

def format_time(t):
    # Convert seconds to h:m:s
    return time.strftime("%H:%M:%S", time.gmtime(t))

#From a DataFrame of k-mers (rows) and multiplicities (values), group by first `kmer_size` bases.
#def aggregate_kmer_multiplicities(dataframe,kmer_size):
#    return dataframe.groupby(dataframe.index.str[:kmer_size]).sum()

def get_genome_length(file_path):
    total_length = 0
    for record in SeqIO.parse(file_path, "fasta"):
        total_length += len(record.seq)
    return total_length

#reads the DoLier output and converts it into a dictionary "kmer": multiplicity 
def dolier_to_dictionary(filepath):
    # Read the file as a tab-separated dataframe with no header
    df = pd.read_csv(filepath, sep='\t', header=None, names=['kmer', 'count'])

    # Convert 'count' column to integer (optional but ensures correct types)
    df['count'] = df['count'].astype(int)

    # Convert to dictionary: kmer as key, count as value
    return df.set_index('kmer')['count'].to_dict()

def run_dolier(input_fasta_path, output_path, kmer_size, threads=1, mismatches=0, verbose=False):
    """ Call to the DoLier script for fast k-mers count"""

    dolier_path = Path('dolier/dolier-kfreqs')

    cmd = [
        dolier_path, #'./dolier/dolier-kfreqs',
        str(input_fasta_path),
        str(output_path),
        str(kmer_size),
        str(mismatches),
        '--kmers',
        '-p', str(threads)
    ]

    stdout = None if verbose else subprocess.DEVNULL

    try:
        subprocess.run(cmd, check=True, stdout=stdout, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"DoLIer failed on {input_fasta_path}")
        print(f"Error: {e.stderr.decode().strip()}")
        raise

def kmer_normalization_by_length(kmer_multiplicities_df, genomes_lengths_series, kmer_size):
    # Calculate the denominator vector: (Length - k + 1) for each genome
    # Index alignment ensures it matches the rows of kmer DataFrame
    normalization_factors = genomes_lengths_series - kmer_size + 1

    # Divide the kmer DataFrame by these factors along the columns (axis=1)
    normalized_df = kmer_multiplicities_df.div(normalization_factors, axis=1)

    return normalized_df

def process_kmers(input_dataset_path, result_folder_path, kmer_size, cpu_processes=2):
        
    dictionary_kmers = dict()
    dictionary_counts = dict()
    genomes_length = dict()

    print(f"\nComputation for kmer of size {kmer_size}")
    print("Finding kmer occurrencies with DoLier:")
    files = [f for ext in ("*.fna", "*.fa", "*.fasta") for f in input_dataset_path.rglob(ext)]
    nof_files = len(files)

    start_time = time.time()


    # Create info file about genome lengths
    for i, filename in enumerate(files, start=1):
        genome_name = filename.name
        # Store a dictionary with both 'label' and 'genome_length'
        genomes_length[genome_name] = {
            'label': filename.parent.name,  # Use .name to get just the folder string (e.g., 'Escherichia')
            'genome_length': get_genome_length(filename)
        }


    # Convert the nested dict to a DataFrame (genomes become the index)
    genomes_length_df = pd.DataFrame.from_dict(genomes_length, orient='index')

    # Sort and save
    genomes_length_df.sort_values(by='genome_length', inplace=True)
    genomes_length_df.to_csv(Path(result_folder_path, "genomes_length.csv"), index=True)


    #DoLier computing kmer occurrences
    for i, filename in enumerate(files, start=1):
        print(f"({i}/{nof_files})\t{filename.parent.stem}\t{filename.name}") 

        genome_name = filename.name
        #genomes_length[genome_name] = get_genome_length(filename)

        # Create a temporary file for DoLIer output
        with tempfile.NamedTemporaryFile(delete=True, mode='w+', suffix=".tsv") as tmpfile:
            tmpfile_path = tmpfile.name

            run_dolier(filename, tmpfile_path, kmer_size, threads=cpu_processes)
            dictionary_kmers[genome_name] = dolier_to_dictionary(tmpfile_path)

    elapsed_time = time.time() - start_time

    print(f"DoLier done! - Execution time: {format_time(elapsed_time)}") #(end_time - start_time):.3f}s")
    print()

    kmer_multiplicities_df = pd.DataFrame.from_dict(dictionary_kmers, orient='columns')

    # Fill missing values with 0 and convert counts to integers
    kmer_multiplicities_df = kmer_multiplicities_df.fillna(0).astype(int)

    # Extract just the 'genome_length' from your nested dictionary into a clean pandas Series
    # This maps genome names directly to their integer lengths
    lengths_series = pd.Series({
        genome: info['genome_length'] for genome, info in genomes_length.items()
    })

    #Normalization by number of possible kmers in the sequence
    kmer_multiplicities_df_normalized = kmer_normalization_by_length(kmer_multiplicities_df, lengths_series, kmer_size)    
    
    # Initialize the results dictionary with the big kmer DataFrames
    results = {
        f'kmer_occurrences_k{kmer_size}': kmer_multiplicities_df,
        f'kmer_occurrences_k{kmer_size}_normalized': kmer_multiplicities_df_normalized
    }

    return results


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Process k-mer occurrences in a dataset of genomes and save the results as csv files."
    )
    
    # Define the command-line arguments
    parser.add_argument(
        '-i', '--dataset_path',       
        type=str, 
        required=True,                
        help="Path to the folder containing the genome dataset (Required)"
    )
    
    parser.add_argument(
        '-k', '--kmer_size', 
        type=int,
        required=True,
        help="The size of the k-mer to analyze (integer)"
    )
    
    parser.add_argument(
        '-p', '--cpu_processes', 
        type=int, 
        default=2,
        help="Number of CPU processes to use for parallel execution (default: 2)"
    )

    # Parse the arguments
    args = parser.parse_args()

    print("[[KMER MULTIPLICITY TOOL: from fasta dataset to kmer multiplicity matrices]]")

    # Convert dataset_path to a Path object first
    dataset_path = Path(args.dataset_path)
    print("Input dataset:",dataset_path)
    
    # dataset_path.name extracts just the last folder name (e.g., 'dataset_1')
    dataset_name = dataset_path.name
    result_folder_path = Path("./results", dataset_name)
    
    # Create the directory
    result_folder_path.mkdir(parents=True, exist_ok=True)
    print(f"Results will be saved to: {result_folder_path}")

    kmer_size = args.kmer_size
    print("kmer size:", kmer_size)
    
    cpu_processes = args.cpu_processes
    print(f"Running execution using {cpu_processes} CPU process(es).")

    # Run the processing function
    kmer_results = process_kmers(dataset_path, result_folder_path, kmer_size=kmer_size, cpu_processes=cpu_processes)

    # Loop through the dictionary and save each DataFrame to a CSV
    for filename, df in kmer_results.items():
        csv_path = Path(result_folder_path, f"{filename}.csv")
        df.to_csv(csv_path, index=True)
        print(f"Saved: {csv_path}")

if __name__ == "__main__":
    main()

