# K-mer Multiplicity Tool

A high-performance containerized Python tool designed to calculate, normalize, and analyze $k$-mer occurrences across genome datasets using the rapid **DoLIer** core frequency engine. 

The tool processes genome assemblies, extracts sequence lengths, counts $k$-mers, and normalizes the results against the total possible number of $k$-mers per genome based on the formula:

$$\text{Genome Length} - k + 1$$

---

## 📋 Prerequisites

Before running this tool, ensure your system has the following dependencies installed:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (and make sure the Docker daemon is actively running)
* A Bash-compatible terminal (Linux, macOS, or Git Bash/WSL on Windows)

---

## Project Structure

Your project directory should match the layout below before building:
```text
your_project/
├── datasets/                   	# Drop your input
├── dolier/
│   └── dolier-kfreqs           	# The core DoLIer binary tool
├── Dockerfile                  	# Container instructions
├── install.sh                  	# Installation script
├── kmer_multiplicity_tool.py   	# Main Python pipeline code
├── launcher_kmer_multiplicity_tool	# Execution script
├── requirements.txt            	# Python library links
├── results/                    	# Generated output folder
└── uninstall.sh                	# Cleanup script
```

## Setup & Installation
To pull the necessary dependencies, set up the container environment, and compile the application image, use the provided installation script:

* Open your terminal in the project directory.

* Grant execution permissions to the install script:


```bash
chmod +x install.sh
./install.sh
```
To verify that the image compiled successfully and is sitting securely in your local Docker registry, run:

```bash
docker images
```

## Running the Tool
Execution is completely automated through the custom ./launcher script, which seamlessly handles directory mapping so your local files safely interact with the isolated container.

Give the launcher script execution permissions:

```bash
chmod +x launcher_kmer_multiplicity_tool
```

Basic Usage Syntax:
```bash
./launcher_kmer_multiplicity_tool -i <dataset_path> -k <kmer_size> [options]
```

## Execution Examples:

Help options:
```bash
./launcher_kmer_multiplicity_tool -h
```

Standard Run: Run using your_dataset_folder of fasta files inside your local ./datasets directory (datasets/your_dataset_folder), targeting a k-mer size of 6, utilizing the default 2 CPU processes. 
Results will automatically generate inside a folder named ./results/your_dataset_folder/:

```bash
./launcher_kmer_multiplicity_tool -i ./dataset -k 6
```

## Uninstallation & System Cleanup
If you need to free up hard drive storage or remove the container entirely from your environment, use the uninstaller script. This script cleanly terminates any stuck container instances, drops the kmer_multiplicity_tool image, and purges dangling layers or build caches:

```bash
chmod +x uninstall.sh
./uninstall.sh
```






