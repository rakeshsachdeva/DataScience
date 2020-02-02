from pdf2image import convert_from_path
try:
    from imageTextExtractor import ImageTextExtractor
except :
    from imageTextExtractor_s import ImageTextExtractor
from PIL import Image
import os,glob,re,csv,configparser
image_block_obj = ImageTextExtractor()
from time import gmtime, strftime
import time
import shutil
import ntpath
import fitz
import datetime

nowTime=strftime("%Y_%m_%d_%H_%M", gmtime())

pdfsOpObj = open('../data/op/ops_pdfs_'+str(nowTime)+'_.csv','w+')
pdfsOpCsv_file= csv.writer(pdfsOpObj)
pdfsOpCsv_file.writerow(["file name","employer list","empr","employee list","empee","id","wc","ss","mw","year"])


config_file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "config", "config.cfg")
if os.path.isfile(config_file_loc) == False:
    raise Exception("Failed to read the Config file from the location: "+str(config_file_loc))

config_obj = configparser.ConfigParser()

try:

    config_obj.read(config_file_loc)
    empr_name1 = (config_obj.get("features","var11"))
    empr_name2 = (config_obj.get("features","var12"))

    emp_id = (config_obj.get("features", "var31"))
    emp_name1 = (config_obj.get("features","var21"))
    emp_name2 = (config_obj.get("features","var22"))

    emp_wto1 = (config_obj.get("features","var4"))
    emp_wto2 = (config_obj.get("features","var41"))
    emp_ssw = (config_obj.get("features","var51"))
    emp_mcw = (config_obj.get("features","var61"))
    emp_mcw2 = (config_obj.get("features","var62"))

    inputPdfFolderPath = (config_obj.get("filepaths","inputPdfFolderPath"))
    ConvertedImgsPath = (config_obj.get("filepaths","ConvertedImgsPath"))
    inputImgsFolderPath = (config_obj.get("filepaths","inputImgsFolderPath"))




    logfilename = config_obj.get("logdata","logfilename")
    #apiPort=config_obj.get("REST","port")
except Exception as e:
    raise Exception("Config file reading error: " + str(e))



class ExtractW2data():
    def __init__(self):
        self.empr_name1=empr_name1
        self.empr_name2=empr_name2
        self.emp_id=emp_id
        self.emp_name1=emp_name1
        self.emp_name2=emp_name2
        self.emp_wto1=emp_wto1
        self.emp_wto2=emp_wto2
        self.emp_ssw=emp_ssw
        self.emp_mcw=emp_mcw
        self.emp_mcw2=emp_mcw2
        self.inputPdfFolderPath=inputPdfFolderPath
        self.ConvertedImgsPath=ConvertedImgsPath
        self.inputImgsFolderPath=inputImgsFolderPath

        self.logfilename=logfilename
        self.TaxStatementYear=["wage and tax","tax statement","w2 & earnings","earnings summary","w-2 tax statement","wage statement","form w-2","filed with employee federal tax return","form w-2 statement","form w-2 summary","w2 tax statement","form w2","form w2 statement","form w2 summary","omb no","local income tax"]
        self.junkHeaders=["11 nonqualified plans","11 nonqualified plans","tax withheld withheld","fed income","fed. income","medicare tax","omb no","omb number","employer id number","w-2 and earnings summary","this summary is included with","social security"," summary wages"]
        self.CompanySuffixes=[" inc "," org "," company "," bank "," llc "," co. "," corporation "," group "]

    def repeats(self,name):
        name = name.replace("&", "").replace("groups llg", "groups llc").replace("group llg", "group llc").replace("§",
                                                                                                                   "")
        for x in range(1, len(name)):
            substring = name[:x]

            if substring * (len(name) // len(substring)) + (substring[:len(name) % len(substring)]) == name:
                return (substring)

        return (name)

    def removePunctuation(self,data):
        # punctuation marks
        punctuations = '''!|()Â§[]{};:'"\<>/?@#$%^&*_~'''

        # traverse the given string and if any punctuation
        # marks occur replace it with null
        for x in data:
            if x in punctuations:
                data = data.replace(x, "").replace("\\'s", "")
                data = re.sub(' +', ' ', data)
                data = re.sub('\.+', '.', data)
                # Print string without punctuation
        return (data.lower().strip())

    def removePattern(self,x):
        x1 = re.compile(r'box\s*[0-9]*\s*of\s*w(-)?2')
        mo = x1.search(x)

        if mo is not None:
            x = x[:mo.start()]
            return (x)
        return x

    def removeJunk(self,x):
        x = self.removePattern(x)

        for junk in self.junkHeaders:
            if junk in x:
                x = x[:x.index(junk)]
            x = re.sub(r'\s*\d+(.)?\d+\s*', ' ', x)
        return x

    def replaceList(self,zeroIndexEmpl):
        zeroIndexEmpl = zeroIndexEmpl.replace("group llg", "group llc").replace("&", "").replace("|. .", "")
        return zeroIndexEmpl

    def extractEmp(self,empdata):
        if len(empdata )>0:
            zeroIndexEmpl = self.removeJunk(" " + empdata[0] + " ")
            if len(zeroIndexEmpl) > 7:
                for comSufx in self.CompanySuffixes:
                    if len(empdata) > 1 and comSufx in " " + empdata[1] + " ":
                        zeroIndexEmpl = zeroIndexEmpl + " " + empdata[1]
                        break

                return self.repeats(zeroIndexEmpl.strip())

            else:
                zeroIndexEmpl = self.removeJunk(" " + empdata[1] + " ")
                for comSufx in self.CompanySuffixes:
                    if len(empdata) > 2 and comSufx in " " + empdata[2] + " ":
                        zeroIndexEmpl = zeroIndexEmpl + " " + empdata[1]
                return self.repeats(zeroIndexEmpl.strip())
        else:
            return ""

    def FilterData(self,Datalist, varlist):
        for er in Datalist[:]:
            for var in varlist[:]:
                if var in er:
                    try:
                        Datalist.remove(er)
                    except:
                        pass

        # Datalist=list(set(Datalist))

        return Datalist

    def getWageData(self,WagesTipsList):
        wags = re.findall(r"\s+[0-9]+\s*\.\s*[0-9]{2}\s+", " " + WagesTipsList + " ")
        return wags

    def WagesFound(self,employerWages):
        if len(employerWages) > 0:
            return employerWages[0]
        else:
            return -9999.99

    def getEmployerIdFirst(self,ListEmplyerId):
        ListEmplyerId = " ".join(ListEmplyerId)
        ListEmplyerId = ListEmplyerId.split(" ")
        employerId = ""
        for eachitem in ListEmplyerId:
            employerId = re.findall("\s+[0-9]{2}\s*\-\s*[0-9]{7}\s+", " " + eachitem + " ")
            employerIdnewPattern = re.findall("\s+[0-9]{9}\s+", " " + eachitem + " ")
            if len(employerId) > 0:
                return employerId[0], True
            elif len(employerId) == 0 and len(employerIdnewPattern) > 0:
                return employerIdnewPattern[0], True
        return employerId, False

    def getEmployerIdnumber(self,eachDataitem):
        employerId = re.findall("\s+[0-9]{2}\s*\-\s*[0-9]{7}\s+", " " + eachDataitem + " ")
        if len(employerId) > 0:
            return employerId[0], True
        else:
            return "", False

    def findYear(self,yearData, isYearFound2):
        StatementYear = ''
        for eachLine in yearData:
            match = re.match(r'(.*(\b[2]\s*[0]\s*[0-9]{1}\s*[0-9]{1}\b))', " " + eachLine + " ")
            # match = re.match(r'(.*(\b[0-9]{2}-[0-9]{7}\b))', x)

            if match is not None:
                StatementYear = match.group(2)
                isYearFound2 = True

                return StatementYear, isYearFound2
        return StatementYear, isYearFound2

    def findyear3(self,pdfPath):
        try:
            doc = fitz.open(pdfPath)
            nowyear = datetime.datetime.now().year
            for pageNum, pageData in enumerate(doc):
                pageData = doc.loadPage(pageNum)
                pageText = pageData.getText("text")
                if len(pageText)>0:
                    for checkYear in range(2000, nowyear):
                        if str(checkYear) in (pageText):
                            return [checkYear]
            return []
        except:
            return []

    def ConvertPdfToImgs(self,eachpdf,page_num):
        PdfImgFolderPath=""
        #print(eachpdf)
        try:
            numberPages = convert_from_path(eachpdf,first_page=page_num,last_page=page_num)
            if len(numberPages)==0:
                numberPages = convert_from_path(eachpdf, first_page=1, last_page=1)

            foldername, file_extension = os.path.splitext(eachpdf)
            foldername = os.path.basename(foldername)
            # foldername=str(i)+"_"+foldername
            #os.rename(eachpdf, inputPdfFolderPath + foldername + file_extension)

            PdfImgFolderPath = ConvertedImgsPath + foldername

            if not os.path.exists(PdfImgFolderPath):
                os.makedirs(PdfImgFolderPath)
            for cnt, page in enumerate(numberPages):
                page.save(PdfImgFolderPath + "/file_" + str(cnt) + ".jpg", "JPEG")
        except Exception as e:
            print(" Failed to extract for :" + str(eachpdf))
            print(e)
            return False
            pass
        return True


    def extractdata(self,foldername):
        extracted_data = {}
        employerName = []
        employeeName = []
        employerId = []
        employerId2 = []
        W2Year = []

        W2YearDate = []

        isEmployerNameFound = False
        isEmployeeNameFound = False
        isEmployerIdFound = False
        isEmployerIdFound2 = False

        isWagesFound = False
        isSSWagesFound = False
        isMediWagesFound = False
        isYearFound = False

        isYearFound2 = False
        employerWages1 = []
        employerWages2 = []
        employerWages3 = []
        pdfFolder=foldername
        ConvertedImages=(glob.glob(str(self.ConvertedImgsPath+pdfFolder)+"/*.jpg"))
        ConvertedImages.sort()
        for eachImg in ConvertedImages:
            try:
                imagefiles = Image.open(eachImg)
                text_seg = image_block_obj.process_image(imagefiles)
                if len(text_seg) > 11 and isYearFound2 == False:
                    StatementYear2, isYearFound2 = self.findYear(text_seg[:5] + text_seg[-5:], isYearFound2)

                for varIndex, eachData in enumerate(text_seg):

                    eachData = self.removePunctuation(eachData)
                    if isEmployerIdFound2 == False:
                        employerId2, isEmployerIdFound2 = self.getEmployerIdnumber(eachData)
                    for eachW2year in self.TaxStatementYear:
                        if eachW2year in eachData and isYearFound == False:
                            W2Year = W2Year + text_seg[varIndex - 2:varIndex + 2]
                            if len(W2Year) > 0:
                                W2YearDate, isYearFound = self.findYear(W2Year, isYearFound)

                    if (self.empr_name1 in eachData or self.empr_name2 in eachData) and (isEmployerNameFound == False):
                        employerName = employerName + text_seg[varIndex + 1:varIndex + 4]
                        isEmployerNameFound = True

                    if (self.emp_name1 in eachData or self.emp_name2 in eachData) and (isEmployeeNameFound == False):
                        employeeName = employeeName + text_seg[varIndex + 1:varIndex + 4]
                        isEmployeeNameFound = True

                    if (self.emp_id in eachData) and (isEmployerIdFound == False):
                        employerId = employerId + text_seg[varIndex + 1:varIndex + 4]
                        isEmployerIdFound = True

                    eachDataforWages = re.sub('[^a-z\s]+', '', eachData).strip()
                    eachDataforWages = re.sub(' +', " ", eachDataforWages)
                    if (self.emp_wto1 in eachDataforWages) and isWagesFound == False:
                        Wages1 =self. getWageData(text_seg[varIndex + 1])
                        if len(Wages1) > 0:
                            employerWages1 = Wages1
                            isWagesFound = True
                            w1p = 1
                    elif (self.emp_wto2 in eachDataforWages) and isWagesFound == False:
                        Wages1 = self.getWageData(text_seg[varIndex + 1])
                        if len(Wages1) > 0:
                            employerWages1 = Wages1
                            isWagesFound = True
                            w1p = 2

                    if (self.emp_ssw in eachDataforWages) and isSSWagesFound == False:
                        Wages2 = self.getWageData(text_seg[varIndex + 1])
                        if len(Wages2) > 0:
                            employerWages2 = Wages2
                            isSSWagesFound = True
                    if (self.emp_mcw in eachDataforWages or self.emp_mcw2 in eachDataforWages) and isMediWagesFound == False:
                        Wages3 = self.getWageData(text_seg[varIndex + 1])
                        if len(Wages3) > 0:
                            employerWages3 = Wages3
                            isMediWagesFound = True

                extracted_data["filename"] = ntpath.basename(foldername)+".pdf"
                extracted_EmployerList = self.FilterData(employerName, [self.empr_name1, self.empr_name2])
                #extracted_data["EmployerList"] = extracted_EmployerList
                extracted_data[empr_name1] = self.extractEmp(extracted_EmployerList)

                extracted_EmployeeList = self.FilterData(employeeName, [self.emp_name1, self.emp_name1])
                #extracted_data["EmployeeList"] = extracted_EmployeeList
                extracted_data[self.emp_name1] = self.extractEmp(extracted_EmployeeList)

                ListEmplyerId = self.FilterData(employerId, [self.emp_id])
                empidList, isEmployerIdFound = self.getEmployerIdFirst(ListEmplyerId)
                if isEmployerIdFound == True and len(empidList) > 0:
                    extracted_data[self.emp_id] = empidList
                elif isEmployerIdFound2 == True and len(employerId2) > 0:
                    extracted_data[self.emp_id] = employerId2
                else:
                    extracted_data[self.emp_id] = ""

                extracted_data[self.emp_wto2] = self.WagesFound(employerWages1)
                extracted_data[self.emp_ssw] = self.WagesFound(employerWages2)
                extracted_data[self.emp_mcw] = self.WagesFound(employerWages3)

                if len([W2YearDate]) > 0:
                    extracted_data["year"] = W2YearDate
                else:
                    extracted_data["year"] = StatementYear2
            except  Exception as e:
                print(e)
                print(" failed to process :" + str(pdfFolder))
                print()
                print()
                pass
        #shutil.rmtree('../data/imgs')
        pdfsOpCsv_file.writerow(extracted_data.values())
        #print(extracted_data)
        return (extracted_data)


    def extract_img_data(self,eachImg):
        extracted_data = {}
        employerName = []
        employeeName = []
        employerId = []
        employerId2 = []
        W2Year = []

        W2YearDate = []

        isEmployerNameFound = False
        isEmployeeNameFound = False
        isEmployerIdFound = False
        isEmployerIdFound2 = False

        isWagesFound = False
        isSSWagesFound = False
        isMediWagesFound = False
        isYearFound = False

        isYearFound2 = False
        employerWages1 = []
        employerWages2 = []
        employerWages3 = []

        try:
            imagefiles = Image.open(eachImg)
            text_seg = image_block_obj.process_image(imagefiles)

            if len(text_seg) > 11 and isYearFound2 == False:
                StatementYear2, isYearFound2 = self.findYear(text_seg[:5] + text_seg[-5:], isYearFound2)

            for varIndex, eachData in enumerate(text_seg):

                eachData = self.removePunctuation(eachData)
                if isEmployerIdFound2 == False:
                    employerId2, isEmployerIdFound2 = self.getEmployerIdnumber(eachData)
                for eachW2year in self.TaxStatementYear:
                    if eachW2year in eachData and isYearFound == False:
                        W2Year = W2Year + text_seg[varIndex - 2:varIndex + 2]
                        if len(W2Year) > 0:
                            W2YearDate, isYearFound = self.findYear(W2Year, isYearFound)

                if (self.empr_name1 in eachData or self.empr_name2 in eachData) and (isEmployerNameFound == False):
                    employerName = employerName + text_seg[varIndex + 1:varIndex + 4]
                    isEmployerNameFound = True

                if (self.emp_name1 in eachData or self.emp_name2 in eachData) and (isEmployeeNameFound == False):
                    employeeName = employeeName + text_seg[varIndex + 1:varIndex + 4]
                    isEmployeeNameFound = True

                if (self.emp_id in eachData) and (isEmployerIdFound == False):
                    employerId = employerId + text_seg[varIndex + 1:varIndex + 4]
                    isEmployerIdFound = True

                eachDataforWages = re.sub('[^a-z\s]+', '', eachData).strip()
                eachDataforWages = re.sub(' +', " ", eachDataforWages)
                if (self.emp_wto1 in eachDataforWages) and isWagesFound == False:
                    Wages1 =self. getWageData(text_seg[varIndex + 1])
                    if len(Wages1) > 0:
                        employerWages1 = Wages1
                        isWagesFound = True
                        w1p = 1
                elif (self.emp_wto2 in eachDataforWages) and isWagesFound == False:
                    Wages1 = self.getWageData(text_seg[varIndex + 1])
                    if len(Wages1) > 0:
                        employerWages1 = Wages1
                        isWagesFound = True
                        w1p = 2

                if (self.emp_ssw in eachDataforWages) and isSSWagesFound == False:
                    Wages2 = self.getWageData(text_seg[varIndex + 1])
                    if len(Wages2) > 0:
                        employerWages2 = Wages2
                        isSSWagesFound = True
                if (self.emp_mcw in eachDataforWages or self.emp_mcw2 in eachDataforWages) and isMediWagesFound == False:
                    Wages3 = self.getWageData(text_seg[varIndex + 1])
                    if len(Wages3) > 0:
                        employerWages3 = Wages3
                        isMediWagesFound = True
            extracted_data["filename"] =ntpath.basename(eachImg)


            extracted_EmployerList = self.FilterData(employerName, [self.empr_name1, self.empr_name2])
            #extracted_data["EmployerList"] = extracted_EmployerList
            extracted_data[empr_name1] = self.extractEmp(extracted_EmployerList)

            extracted_EmployeeList = self.FilterData(employeeName, [self.emp_name1, self.emp_name1])
            #extracted_data["EmployeeList"] = extracted_EmployeeList
            extracted_data[self.emp_name1] = self.extractEmp(extracted_EmployeeList)

            ListEmplyerId = self.FilterData(employerId, [self.emp_id])
            empidList, isEmployerIdFound = self.getEmployerIdFirst(ListEmplyerId)
            if isEmployerIdFound == True and len(empidList) > 0:
                extracted_data[self.emp_id] = empidList
            elif isEmployerIdFound2 == True and len(employerId2) > 0:
                extracted_data[self.emp_id] = employerId2
            else:
                extracted_data[self.emp_id] = ""

            extracted_data[self.emp_wto2] = self.WagesFound(employerWages1)
            extracted_data[self.emp_ssw] = self.WagesFound(employerWages2)
            extracted_data[self.emp_mcw] = self.WagesFound(employerWages3)

            if len([W2YearDate]) > 0:
                extracted_data["year"] = W2YearDate
            else:
                extracted_data["year"] = StatementYear2
        except  Exception as e:
            print(e)
            print(" failed to process :" + str(eachImg))
            print()
            print()
            pass
        #shutil.rmtree('../data/imgs')
        pdfsOpCsv_file.writerow(extracted_data.values())
        #print(extracted_data)
        return (extracted_data)

    def process_w2(self,eachpdf,page_num):
        tempfetaures={}
        tempfetaures["filename"] = os.path.basename(eachpdf)
        # featurelist=['employer name','employee name', 'employer id number', 'wages tips other comp', 'social security wages', 'medicare wages and tips']
        # for xfeature in featurelist:
        #     tempfetaures[xfeature]=""
        tempfetaures["employer name"] = " "
        tempfetaures["employee name"] = " "
        tempfetaures["employer id number"] = " "
        tempfetaures["wages tips other comp"] = -9999.99
        tempfetaures["social security wages"] = -9999.99
        tempfetaures["medicare wages and tips"] = -9999.99
        tempfetaures["year"] = []




        try:
            isImagesCreated = (self.ConvertPdfToImgs(eachpdf,page_num))
            if isImagesCreated:
                pfilename, pfile_extension = os.path.splitext(eachpdf)
                imgPdfsPath = os.path.basename(pfilename)
                fetaures = self.extractdata(imgPdfsPath)
                shutil.rmtree(self.ConvertedImgsPath)


                if fetaures['year']=='' or fetaures['year']==[]:
                    year3=self.findyear3(eachpdf)
                    if len(year3)>0:
                        fetaures['year']=[str(year3[0])]
                    else:
                        fetaures['year']=['']
                    return fetaures
                else:
                    return fetaures
            else:
                return tempfetaures
        except:
            return tempfetaures


if __name__== "__main__" :
    obj=ExtractW2data()
    strtTime=time.time()
    eachpdf="/Users/rsachdeva/Documents/pythonProjs/W2/0064O00000jttNLQAY-00P4O00001JjOs8UAF-salvatore_rabito_w2_or_1040_or.PDF"
    print(obj.process_w2(eachpdf,12))

    #imgsData=glob.glob("../data/w2_imgs/*.jpg") +glob.glob("../data/w2_imgs2/*.jpeg")+glob.glob("../data/w2_imgs2/*.png")

    # eachimg="/Users/rsachdeva/Documents/pythonProjs/w2_29Oct/W2_data/New_W2/0064O00000jfdbsQAA-00P4O00001Kmgr4UAB-Richard Winkleblack - W2 -1.jpg"
    # y= obj.extract_img_data(eachimg)
    # print(y)
    # endTime=time.time()
    # print(endTime-strtTime)