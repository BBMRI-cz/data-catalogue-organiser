import requests

res = requests.get("https://api.orphadata.com/rd-cross-referencing/icd-10s/c19")
print(res.json())

for i in range(100):
    res = requests.get(f"https://api.orphadata.com/rd-cross-referencing/icd-10s/c{str(i).zfill(2)}")
    print("------------------")
    if "data" in res.json():
        for val in res.json()["data"]["results"]:
            print(str(i).zfill(2),val["ORPHAcode"], val["Preferred term"])
    else:
        print("no Info for ", str(i).zfill(2))