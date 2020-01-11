import requests
import os,glob
url="http://0.0.0.0:1999/extract-w2-data"
import json
import csv

employ_data = open('../data/EmployData_0512.csv', 'w')

csvwriter = csv.writer(employ_data)

def requestResponse(filesData,count):
    resp = requests.post(url, json=filesData,headers={"content-type":"application/json"})
    response = resp.text
    json_parsed = json.loads(response)

    emp_data=(json_parsed['data'][0])
    if count == 0:
        header = emp_data.keys()

        csvwriter.writerow(header)

        count += 1

    csvwriter.writerow(emp_data.values())


InputFiles=glob.glob("../data/W2/*.*")

for indx,eachfile in enumerate(InputFiles):
    eachfile="/Users/rsachdeva/Documents/pythonProjs/formW2/w2_img_data_single/data/W2/"+str(os.path.basename(eachfile))
    print(eachfile)
    filesData={"data":[{"filePath":eachfile,"documentId":indx}]}
    requestResponse(filesData,indx)

employ_data.close()



