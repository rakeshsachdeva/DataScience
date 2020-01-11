import requests,glob,os,json
files=glob.glob("New_W2/*.*")
files=files[:2]
print(os.getcwd())
print(files)
headers = {'content-type': 'application/json'}

for i,eachfile in enumerate(files):
    eachfile=str(os.getcwd())+"/"+eachfile
    print(eachfile)
    PARAMS={"filePath":eachfile,"documentId":i}
    r = requests.post(url = "http://0.0.0.0:1999/extract-w2-data", data = json.dumps(PARAMS),headers=headers)
    print(r.text)
