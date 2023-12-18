# data-catalogue-organiser
This is the repository for the oragnisation part of the BBMRI.cz data catalog.

# Organisation

### MiSEQ
Collect pseudonymized data, organises the data to a specific folder hierarchy, collects metadata for the catalogue and uploads the metadata to data.bbmri.cz

The whole pipeline is managed in `pipeline.py`:

1. Data are organised using class **RunOrganiser** defined in `organise_run.py`
2. The metadata of the whole run are collected using class **CollectRunMetadata** defined in `miseq_run_metadata.py`
3. For each sample in the run specific metadata are collected by class **CollectSampleMetadata** defined in `miseq_sample_metadata.py`
4. Uploading the data to the data.bbmri.cz catalogue using class **MolgenisImporter** defined in `import_metadata.py`

Additional files: 

`manage_libraries.py` - This file extracts specific details about the libraries used for sequencing and more additional information.