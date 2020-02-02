import requests
import os,glob
url="http://0.0.0.0:1999/extract-w2-data"
import json
import csv

employ_data = open('../data/EmployData_27012020_5.csv', 'w')

csvwriter = csv.writer(employ_data)

def requestResponse(filesData,count):
    files={}
    files["file_x"]=filesData['data'][0]['filePath']
    resp = requests.post(url, json=filesData,headers={"content-type":"application/json"})
    response = resp.text
    json_parsed = json.loads(response)
    emp_data=(json_parsed['data'][0])
    if count == 0:
        header = emp_data.keys()

        csvwriter.writerow(header)

        count += 1
    x1=list(files.values())+list(emp_data.values())
    csvwriter.writerow(x1)


InputFiles=glob.glob("/Users/rsachdeva/Documents/pythonProjs/W2/*.*")
# checkFiles=["0064O00000kIAogQAG-00P4O00001KCJloUAH-devindra2w2.jpg","0060B00000iAQtDQAW-00P4O00001KBNeJUAX-Donald Wilczynski blurry W2, P.pdf","0064O00000kBxw0QAC-00P4O00001Jkz8mUAB-TheresaW2.jpg","0064O00000k8xqdQAA-00P4O00001JjcgmUAB-Timothy Lawyer - W2.jpg","0064O00000k8xqTQAQ-00P4O00001JlNNnUAN-Anderson Owens Previous Job W2.jpg","0064O00000k7uGaQAI-00P4O00001JjLDYUA3-floatlifeW2.pdf","0064O00000kC41NQAS-00P4O00001JkuKAUAZ-Richard Knowles W2.jpg","0060B00000iAQtDQAW-00P4O00001KBNduUAH-Donald Wilczynski 2018 W2.pdf","0064O00000kHlB5QAK-00P4O00001KBqxzUAD-jospeh W2.jpg","0064O00000k8yRjQAI-00P4O00001Jk0BaUAJ-Tiffany Menzia - HUSBAND W2.JPG","0064O00000kBV8QQAW-00P4O00001Jk7qJUAR-lamaW2.jpg","0064O00000k9I2dQAE-00P4O00001Jk4KCUAZ-Douglas Werdebaugh  PS, W2, VA.pdf","0064O00000kALKgQAO-00P4O00001JkZkLUAV-W2.jpg","0064O00000aDlOMQA0-00P4O00001JkXqNUAV-Brenton Dyer - W2.pdf","0064O00000kBCdgQAG-00P4O00001Jjv0AUAR-miguena 2018 w2.jpg","0064O00000kH5WEQA0-00P4O00001KBPAxUAP-Ismael Salgado 2017 W2.jpeg","0064O00000k6gEFQAY-00P4O00001KCDu7UAH-check stubs _ w2.pdf","0064O00000kAhsQQAS-00P4O00001JjaBpUAJ-PorterW2.jpg","0064O00000k5JHdQAM-00P4O00001KBOS9UAP-jordanw21.jpg","0064O00000k8xtUQAQ-00P4O00001JjTTjUAN-MArianne W2.jpg","0064O00000k8y33QAA-00P4O00001JkOBAUA3-Deborah Smith W2.jpg","0064O00000kBbgeQAC-00P4O00001JlGBGUA3-Kathleen Knight W2.pdf","0064O00000kGnz3QAC-00P4O00001KBpqlUAD-Eileen Prev employer and curre.pdf","0064O00000kHSALQA4-00P4O00001KBNYqUAP-Meredith Baker W2 previous emp.jpg","0064O00000aDlOMQA0-00P4O00001JkXqIUAV-Brenton Dyer - W2.pdf","0064O00000k5OD0QAM-00P4O00001JlLgcUAF-Heather Kalks W2.pdf","0064O00000kAjdIQAS-00P4O00001JjRA3UAN-Matthew Hader Previous W2.jpg","0064O00000kIAogQAG-00P4O00001KCJlyUAH-devindra1w2.jpg","0064O00000kC3YFQA0-00P4O00001KBOCzUAP-W2 Form.pdf","0064O00000kCQyyQAG-00P4O00001KC0UAUA1-Delberto W2 taxes .pdf","0064O00000kAAknQAG-00P4O00001KCJYpUAP-Tony Craig W2.pdf","0064O00000kBpo4QAC-00P4O00001KBvXsUAL-americaw2.pdf","0064O00000kAuEJQA0-00P4O00001JkjQnUAJ-W2-MO.jpg","0064O00000kBbgeQAC-00P4O00001JlGBDUA3-Kathleen Knight W2.pdf","0064O00000kHmMXQA0-00P4O00001KCKUnUAP-Nathan Storm Spouse PS W2.pdf","0064O00000k8xxkQAA-00P4O00001JjfMpUAJ-Stacey Humphrey W2.pdf","0064O00000kADHAQA4-00P4O00001Jjf3LUAR-Richard Brouhard W2.png","0064O00000k8y1dQAA-00P4O00001JjnqlUAB-Andrew Gose cut off W2, UB and.pdf","0064O00000kHXUJQA4-00P4O00001KBV8CUAX-shanon 2018 w2.jpg","0064O00000kB09tQAC-00P4O00001Jk4QJUAZ-2018 W2.jpg","0064O00000kBxwSQAS-00P4O00001KBLlJUAX-andrea V  2017  W2.jpg","0064O00000kBgjBQAS-00P4O00001Jkyv0UAB-Anthony Caruso W2.pdf","0064O00000k6gEFQAY-00P4O00001KByHTUA1-check stubs _ w2.pdf","0064O00000k8yLiQAI-00P4O00001Jkav8UAB-KC Parks VC, W2, DL.pdf","0064O00000kBbgeQAC-00P4O00001JlGB5UAN-Kathleen Knight W2.pdf","0064O00000kBbgeQAC-00P4O00001JlGBCUA3-Kathleen Knight W2.pdf","0064O00000kI72JQAS-00P4O00001KCLuxUAH-w2 jeanne stock.jpg","0064O00000kAyESQA0-00P4O00001Jjbt0UAB-ortizW2.pdf","0064O00000aDmSjQAK-00P4O00001JkSvEUAV-chetram w2 2017.jpg","0064O00000kArVqQAK-00P4O00001KBeSOUA1-David Black 2018 W2.jpg"]


filesProcess=[]
for indx,eachfile in enumerate(InputFiles):
    filesProcess.append(str(os.path.basename(eachfile)))

# RunFiles = list(set(filesProcess) & set(checkFiles))
#print(len(filesProcess), len(checkFiles), len(RunFiles))

with open("/Users/rsachdeva/Documents/pythonProjs/formW2/w2_img_data_single/data/W2CLassifyResults.csv","r") as fl:
    requestsdata=fl.readlines()


for indx, eachfile in enumerate(InputFiles):
    for x in requestsdata:
        x=x.split(",")
        filn=x[0]
        inpf=str(os.path.basename(eachfile))
        if filn.lower()==inpf.lower():
            title = x[1]
            if title=="w2":
                try:
                    page_num = int(str(x[2].replace("\n", "")))
                except:
                    page_num = 0
            else:
                page_num = 0

            print(indx)
            eachfile="/Users/rsachdeva/Documents/pythonProjs/W2/"+str(os.path.basename(eachfile))

            filesData={"data":[{"filePath":eachfile,"documentId":indx,"page_num":page_num+1}]}
            requestResponse(filesData,indx)

employ_data.close()



