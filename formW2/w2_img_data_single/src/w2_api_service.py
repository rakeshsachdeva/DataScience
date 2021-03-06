# encoding: utf-8
# Greeting Bot
# Authors: <Rakesh Sachdeva <Rakesh.Sachdeva@careerbuilder.com>> <Singh, Prashant <Prashant.Singh@careerbuilder.com>>
'''
This library implement algorithm for greetings messages.

'''
####### Internal Library Import
import configparser
from extract_w2data import ExtractW2data
import shutil,re

###### Generic Library Import
import sys
sys.path.insert(0, "../../")
# reload(sys)
# sys.setdefaultencoding('utf8')
from flask import Flask, jsonify
import json, requests
from flask_cors import CORS, cross_origin
from flask import json
from flask.globals import request
import os

testfile=open("../test_valiresults1.csv","a")

config_file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "config", "config.cfg")
if os.path.isfile(config_file_loc) == False:
    raise Exception("Failed to read the Config file from the location: "+str(config_file_loc))

config_obj = configparser.ConfigParser()
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

try:

    config_obj.read(config_file_loc)
    server_add = (config_obj.get("serverdetails","server_add"))
    port_num = (config_obj.get("serverdetails","port_num"))
    inputPdfFolderPath = (config_obj.get("filepaths","inputPdfFolderPath"))
    inputImgsFolderPath = (config_obj.get("filepaths","inputImgsFolderPath"))
    ConvertedImgsPath = (config_obj.get("filepaths","ConvertedImgsPath"))

    logfilename = config_obj.get("logdata","logfilename")
    #apiPort=config_obj.get("REST","port")
except Exception as e:
    raise Exception("Config file reading error: " + str(e))

app = Flask(__name__)
CORS(app)
w2_obj=ExtractW2data()
print(w2_obj)
def Merge(status, response):
    return(status.update(response))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def year_response(responseYear):
    if len(responseYear) == 0:
        return 0
    if isinstance(responseYear,list) and len(responseYear)>0:
        responseYear=responseYear[0]
    elif isinstance(responseYear, list) and len(responseYear) == 0:
        return 0
    responseYear = responseYear.replace(" ", "")
    if len(responseYear) == 4 and isinstance(int(responseYear), int):
        return int(responseYear)
    else:
        return  0

def wages_response(wages):
    if  wages==0:
        return 0.00

    wages=wages.replace(" ","")
    if re.findall(r"\s+[0-9]+\s*\.\s*[0-9]{2}\s+", " " + str(wages) + " ") or int(wages)==0:
        return float("{0:.2f}".format(float(wages)))

    else:
        return 0.00

def empid_response(empidres):
    if len(empidres)==0:
        return ""

    if isinstance(empidres,list)  and len(empidres)>0:
        empidres=empidres[0]
    elif isinstance(empidres,list)  and len(empidres)==0:
        return ""

    empidres=empidres.replace(" ","")

    if re.findall("\s+[0-9]{2}\s*\-\s*[0-9]{7}\s+", " " + empidres + " ") or re.findall("\s+[0-9]{9}\s+"," " + empidres + " "):
        return empidres
    else:
        return  ""

def w2_str_features(responseFeature,mincharlimit):
    if isinstance(responseFeature,str)==True and len(responseFeature)>mincharlimit:
        return responseFeature
    else:
        return ""




def validate_response(responsedata,inpfilename,uniqid,docid):
    validated_res={}
    print(responsedata)
    validated_res["documentId"]=docid
    validated_res["filename"]=inpfilename
    validated_res["uniqueId"]=uniqid
    validated_res["employerName"]=w2_str_features(responsedata["employer name"],mincharlimit=3)
    validated_res["employeeName"]=w2_str_features(responsedata["employee name"],mincharlimit=5)
    validated_res["filename"]=w2_str_features(inpfilename,mincharlimit=21)
    validated_res["year"]=year_response(responsedata["year"])
    validated_res["employerIdNumber"]= empid_response(responsedata["employer id number"])
    validated_res["wagesTipsOtherComp"]=wages_response(responsedata["wages tips other comp"])
    validated_res["socialSecurityWages"]=wages_response(responsedata["social security wages"])
    validated_res["medicareWageAndTips"]=wages_response(responsedata["medicare wages and tips"])
    testfile.write(str(inpfilename)+","+str(uniqid)+","+
                   str(responsedata["employer name"])+","+str(validated_res["employerName"])+","+
                   str(responsedata["employee name"])+","+str(validated_res["employeeName"])+","+
                   str(responsedata["year"])+","+str(validated_res["year"])+","+
                   str(responsedata["employer id number"])+","+str(validated_res["employerIdNumber"])+","+
                   str(responsedata["wages tips other comp"])+","+str(validated_res["wagesTipsOtherComp"])+","+
                   str(responsedata["social security wages"])+","+str(validated_res["socialSecurityWages"])+","+
                   str(responsedata["medicare wages and tips"])+","+str(validated_res["medicareWageAndTips"])+","+
                   "\n")


    return validated_res


#
# # ------------------------------------------------------------------------------------------------------------------------------------
@app.route('/extract-w2-data', methods=['POST'])
@cross_origin()
def processw2Api():
    if request.method != 'POST':
        apireponse={"status":  101, "error": "Only accept POST request"}
        Merge(apireponse,{})
        return json.dumps({"data":[apireponse]})

    if not request.headers['Content-Type'] == 'application/json':
        apireponse={"status":102, "error": "Only accept Content-Type:application/json in headers"}
        Merge(apireponse,{})
        return json.dumps({"data":[apireponse]})

    if not request.is_json :
        apireponse={"status":  103, "error": 'Content_Type should be applicatin/json,Expecting json data key as : {"filename":"filepath"}' }
        Merge(apireponse,{})
        return json.dumps({"data":[apireponse]})

    if 'filePath' not in request.json and 'documentId' not in request.json:
        apireponse = {"status": 104,
                      "error": ' Expecting json data key as : {"filePath":"w2_file_path","documentId":"xxx123"}'}
        Merge(apireponse, {})
        return json.dumps({"data": [apireponse]})




    try:
        inpfilename = request.json['filePath']
        docid=request.json['documentId']
        if os.path.isfile(inpfilename)==False:
            apireponse = {"status": 105,
                          "error": ' file not exist as given path '}
            Merge(apireponse, {})
            return json.dumps({"data": [apireponse]})

        pfilename, pfile_extension = os.path.splitext(inpfilename)

        uniqid = os.path.basename(pfilename).split("-")[0]
        if len(uniqid)!=18:
            apireponse = {"status": 106,
                          "error": ' extracted unique id is of not of len: 18 chars '}
            Merge(apireponse, {})
            return json.dumps({"data": [apireponse]})


        if pfile_extension.lower() == ".pdf":
            responseData = w2_obj.process_w2(inpfilename)
            validated_response = validate_response(responseData,inpfilename,uniqid,docid)
            apireponse = {"status": 100, "error": ""}
            Merge(apireponse, validated_response)
            return json.dumps({"data": [apireponse]})


        elif pfile_extension.lower() in [".jpg", ".jpeg", ".png"]:
            responseData = w2_obj.extract_img_data(inpfilename)
            validated_response=validate_response(responseData,inpfilename,uniqid,docid)
            apireponse = {"status": 100, "error": ""}
            Merge(apireponse, validated_response)
            return json.dumps({"data": [apireponse]})

        else:
            apireponse={"status": 107,"error": 'Expecting file formats : jpeg, jpg, png or pdf  '}
            Merge(apireponse, {})
            return json.dumps({"data":[apireponse]})

    except Exception as e:
        apireponse={"status": 108, "error": 'W2  extraction error'}
        Merge(apireponse,{})
        return json.dumps({"data":[apireponse]})





if __name__ == '__main__':
    app.run(server_add, port=(port_num), debug=False, threaded=True)

    # import requests, glob, os, json
    #
    # files = glob.glob("New_W2/*.*")
    # print(len(files))
    #
    # for index,x in enumerate(files):
    #     pfilename,pfile_extension=os.path.splitext(x)
    #     (pfilename)=str(os.getcwd()+"/"+x)
    #     if pfile_extension.lower() == ".pdf":
    #         responseData = w2_obj.process_w2(pfilename)
    #         validated_response = validate_response(responseData, pfilename, index, index)
    #         apireponse = {"status": 100, "error": ""}
    #     elif pfile_extension.lower() in [".jpg", ".jpeg", ".png"]:
    #         responseData = w2_obj.extract_img_data(pfilename)
    #         validated_response = validate_response(responseData, pfilename,  index, index)


