[![DOI](https://zenodo.org/badge/682957571.svg)](https://doi.org/10.5281/zenodo.10408794)
# data-catalogue-organiser
This is the repository for the oragnisation part of the BBMRI.cz data catalog.

## Organisation
Organises pseudonymized sequencing files into the following structure:
- OrganisedRuns
  - year
    - sequencing_type
      - run_number

## Supported sequencing types
Miseq, New Miseq, MammaPrint

## How to run the scripts
### Locally - Development
#### Using main.py
1. Install requirements
```bash
pip install -r requiremenents.txt
```
2. Run main.py
```bash
python main.py -r path/to/pseudonymized/runs/folder  -o /path/to/root/organisation/folder -p /path/to/patients/folder
```
#### Using docker-compose
```bash
docker-compose up -f compose.yml -d --build
```
### In production
Production is running on Kubernetes cluster SensitiveCloud
#### Using kubernetes (kubectl)
Deploy dependent secrets
```bash
kubectl apply -f kubernetes/organiser-secret.yaml -n bbmri-mou-ns
```
```bash
kubectl apply -f kubernetes/organiser-job.yaml -n bbmri-mou-ns
```
#### Deploying new version in production
Build new docker image
```bash
docker build --no-cache <public-dockerhub-repository>/data-catalogue-organiser:<version> .
docker push <public-dockerhub-repository>/data-catalogue-organiser:<version> 
# change version in kubernetes/organiser-job.yaml
```
#### Debigging
You can visit kubernetes UI [Rancher](https://rancher.cloud.trusted.e-infra.cz/) find the failing pod and investigate in logs.
On how to use Rancher and SensitiveCloud visit [Docs](https://docs.cerit.io/en/platform/overview)

Other option is running a testing job and investigation inside the cluster filemanager (to check user permissions etc.)
```bash
kubectl apply kubectl apply -f kubernetes/testing-job.yaml -n bbmri-mou-ns
```
Then connect to terminal of this job/pod on [Rancher](https://rancher.cloud.trusted.e-infra.cz/)
