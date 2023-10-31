import csv

with open('85021_installations_2023-03-29-2023-03-31_full.csv', errors='replace') as f:
    reader = csv.reader(f)
    for l in reader:
        pass