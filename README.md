# Metrics and Impact Reporting Project 

This repo has two main functions: 
- Retrieving publications using ALA data resources from GBIF
- Retrieving metrics for publications with a DOI

The set-up steps to be able to run all parts of the code are below; then the details for each function are outlined. 

## Set up 
Clone the repo with the command 
```
git clone https://github.com/AtlasOfLivingAustralia/ala-metrics-and-impact.git
```

Once the clone is complete, enter the directory containing the code: 
```
cd ala-metrics-and-impact
```

You will need `python3` and `pip` installed on your machine, and ideally a virtual environment manager. `pipenv` will be used as the example in this project. 
To install `pipenv` run: 
```
pip install pipenv
```
If this doesn't work try
```
pip3 install pipenv
```

To check that `pipenv` is correctly installed, run: 
```
pipenv --version
```

Now use the `Pipfile` in the repository to create a file with all the necessary dependencies. 
```
pipenv install
```

Once everything has installed you can enter the virtual environment using: 
```
pipenv shell
``` 

You're ready to run the code! 
Once you've finished everything you can exit the environment with 
```
exit
```

## Retrieving publications using ALA data resources from GBIF
The main code to retrieve the publication data is in `gbif_publication_data.py`. To start the program, run: 
```
python gbif_publication_data.py
```
When the program has finished you will see two additional files in the folder: 
- `gbif_registry_keys.csv`, which contains a list of data resources with, if they exist, the values of te `gbifRegistryKey`, `doi`, and `gbifDoi` from the data resource metadata
- `publications_from_gbif.csv`, which contains a list of all *unique* publications found from gbif, with publication metadata

## Retrieving metrics for publications with a DOI 

Before you can retrieve publication data you'll need a list of publications with DOIs. 

To retrieve this list from zotero you can run the `zotero.py` script, which will fetch all publications and output them into a file of your choice. 
```
python zotero.py OUTPUT_FILE
```

Once you've got a list of DOIs run the following command with the file with the list of DOIs.
```
python metrics.py INPUT_FILE
```
This will create a `metrics_publications.csv` file with the metrics for all publications.
