from pdf2image import convert_from_path
try:
    from imageTextExtractor import ImageTextExtractor
except :
    from imageTextExtractor_s import ImageTextExtractor
from PIL import Image
import os,glob,re,csv
image_block_obj = ImageTextExtractor()
from time import gmtime, strftime
nowTime=strftime("%Y_%m_%d_%H_%M", gmtime())
#combinations=employers,employer

#var1="employers name address and zip code"
#var1=    "employer name address and zip code"
var12=   "employer name address and zip code"
var11=   "employer name"


#var2=    "employee name address and zip code"
var22=    "employee name address and zip code"
var21=   "employee name"


var31=    "employer id number"

var4="wages tips other comp federal income tax"
var41="wages tips other comp"
var51="social security wages"
var61="medicare wages and tips"
var62="medicare wages andtips"
TaxStatementYear=["wage and tax","tax statement","w2 & earnings","earnings summary","w-2 tax statement","wage statement","form w-2","filed with employee federal tax return","form w-2 statement","form w-2 summary","w2 tax statement","form w2","form w2 statement","form w2 summary","omb no","local income tax"]
junkHeaders=["11 nonqualified plans","11 nonqualified plans","tax withheld withheld","fed income","fed. income","medicare tax","omb no","omb number","employer id number","w-2 and earnings summary","this summary is included with","social security"," summary wages"]
CompanySuffixes=[" inc "," org "," company "," bank "," llc "," co. "," corporation "," group "]
inputFolderPath="../data/pdfs/"
ConvertedImgsPath="../data/imgs/"

pdfsOpObj = open('../data/op/ops_pdfs_'+str(nowTime)+'_.csv','w+')
pdfsOpCsv_file= csv.writer(pdfsOpObj)
pdfsOpCsv_file.writerow(["file name","employer list",var12,"employee list",var22,var31,var41,var51,var61,"year"])

# ImgsOpObj = open('../data/op/ops_images_'+str(nowTime)+'_.csv','w+')
# ImgOpCsv_file = csv.writer(ImgsOpObj)
# ImgOpCsv_file.writerow(["file name","employer list",var12,"employee list",var22,var31,var4,var5,var6,"year","year2"])

def repeats(name):
    name=name.replace("&","").replace("groups llg","groups llc").replace("group llg","group llc").replace("§","")
    for x in range(1, len(name)):
        substring = name[:x]

        if substring * (len(name) // len(substring)) + (substring[:len(name) % len(substring)]) == name:
            return (substring)

    return (name)



def removePunctuation(data):
    # punctuation marks
    punctuations ='''!|()Â§[]{};:'"\<>/?@#$%^&*_~'''

    # traverse the given string and if any punctuation
    # marks occur replace it with null
    for x in data:
        if x in punctuations:
            data = data.replace(x, "").replace("\\'s","")
            data=re.sub(' +', ' ',data)
            data=re.sub('\.+', '.',data)
            # Print string without punctuation
    return (data.lower().strip())


def removePattern(x):
    x1 = re.compile(r'box\s*[0-9]*\s*of\s*w(-)?2')
    mo = x1.search(x)

    if mo is not None:
        x = x[:mo.start()]
        return (x)
    return x


def removeJunk(x):
    x = removePattern(x)

    for junk in junkHeaders:
        if junk in x:
            x = x[:x.index(junk)]
        x = re.sub(r'\s*\d+(.)?\d+\s*', ' ', x)
    return x


def replaceList(zeroIndexEmpl):
    zeroIndexEmpl=zeroIndexEmpl.replace("group llg","group llc").replace("&","").replace("|. .","")
    return zeroIndexEmpl

def extractEmp(empdata):
    zeroIndexEmpl= removeJunk(" "+empdata[0]+" ")
    if len(zeroIndexEmpl)>7 :
        for comSufx in CompanySuffixes:
            if len(empdata)>1 and comSufx in " "+empdata[1]+" ":
                zeroIndexEmpl= zeroIndexEmpl+" "+ empdata[1]
                break

        return repeats(zeroIndexEmpl.strip())

    else:
        zeroIndexEmpl= removeJunk(" " + empdata[1] + " ")
        for comSufx in CompanySuffixes:
            if len(empdata)>2 and comSufx in " "+empdata[2]+" ":
                zeroIndexEmpl= zeroIndexEmpl+" "+ empdata[1]
        return repeats(zeroIndexEmpl.strip())




def FilterData(Datalist,varlist):
    for er in Datalist[:]:
        for var in varlist[:]:
            if var in er:
                try:
                    Datalist.remove(er)
                except:
                    pass


    #Datalist=list(set(Datalist))

    return Datalist

def getWageData(WagesTipsList):
    wags = re.findall(r"\s+[0-9]+\s*\.\s*[0-9]{2}\s+"," "+WagesTipsList+" ")
    return wags

def WagesFound(employerWages):
    if len(employerWages) > 0:
        return employerWages[0]
    else:
        return 0

def getEmployerIdFirst(ListEmplyerId):
    ListEmplyerId = " ".join(ListEmplyerId)
    ListEmplyerId = ListEmplyerId.split(" ")
    employerId=[]
    employerIdnewPattern=[]
    for eachitem in ListEmplyerId:
        employerId=re.findall("\s+[0-9]{2}\s*\-\s*[0-9]{7}\s+"," "+eachitem+" ")
        employerIdnewPattern = re.findall("\s+[0-9]{9}\s+"," "+eachitem+" ")
        if len(employerId)>0 :
            return employerId,True
        elif len(employerId)==0 and len(employerIdnewPattern)>0:
            return employerIdnewPattern,True
    return employerId,False

def  getEmployerIdnumber(eachDataitem):
    employerId = re.findall("\s+[0-9]{2}\s*\-\s*[0-9]{7}\s+", " "+eachDataitem+" ")
    if len(employerId) > 0:
        return employerId,True
    else:
        return "",False


def findYear(yearData,isYearFound2):
    StatementYear=''
    for eachLine in yearData:
        match = re.match(r'(.*(\b[2]\s*[0]\s*[0-9]{1}\s*[0-9]{1}\b))', " "+eachLine+" ")
        #match = re.match(r'(.*(\b[0-9]{2}-[0-9]{7}\b))', x)

        if match is not None:
            StatementYear=match.group(2)
            isYearFound2=True

            return StatementYear,isYearFound2
    return StatementYear,isYearFound2

def ConvertPdfToImgs(inputFolderPath):
    pdfFiles=glob.glob(inputFolderPath+"*.pdf")
    print(len(pdfFiles))


    #filenames = [f for f in os.listdir(inputFolderPath) if os.path.isfile(os.path.join(inputFolderPath, f))]
    for i,eachpdf in enumerate(pdfFiles):
        try:
            numberPages = convert_from_path(eachpdf)
            foldername, file_extension = os.path.splitext(eachpdf)
            foldername=os.path.basename(foldername)
            #foldername=str(i)+"_"+foldername
            os.rename(eachpdf,inputFolderPath+foldername+file_extension)

            PdfImgFolderPath=ConvertedImgsPath+foldername

            if not os.path.exists(PdfImgFolderPath):
                os.makedirs(PdfImgFolderPath)
            for cnt, page in enumerate(numberPages):
                page.save(PdfImgFolderPath+"/file_" + str(cnt) + ".jpg", "JPEG")
        except Exception as e:
            print(" Failed to extract for :"+str(eachpdf))
            print(e)
            pass
    print(" images converted")







def ExtractDataFomConvertedImages(ConvertedImgsPath):
    opData={}
    for pdfFolder in os.listdir(ConvertedImgsPath) :
        extracted_data={}
        employerName=[]
        employeeName=[]
        employerId=[]
        employerId2=[]
        W2Year=[]

        W2YearDate=[]

        isEmployerNameFound=False
        isEmployeeNameFound=False
        isEmployerIdFound=False
        isEmployerIdFound2=False

        isWagesFound=False
        isSSWagesFound=False
        isMediWagesFound=False
        isYearFound=False

        isYearFound2=False
        Wages1=[]
        Wages2=[]
        Wages3=[]

        employerWages1 = []
        employerWages2 = []
        employerWages3 = []
        w1p = 0

        ConvertedImages=glob.glob(str(ConvertedImgsPath+pdfFolder)+"/*.jpg")
        for eachImg in ConvertedImages:
            try:
                extracted_data["file"]=pdfFolder
                imagefiles = Image.open(eachImg)
                text_seg = image_block_obj.process_image(imagefiles)
                if len(text_seg)>11 and isYearFound2==False:
                    StatementYear2,isYearFound2=findYear(text_seg[:5]+text_seg[-5:],isYearFound2)

                for varIndex,eachData in enumerate(text_seg):

                    eachData=removePunctuation(eachData)
                    if isEmployerIdFound2==False:
                        employerId2,isEmployerIdFound2=getEmployerIdnumber(eachData)
                    for eachW2year in TaxStatementYear:
                        if eachW2year in eachData and isYearFound==False:
                            W2Year = W2Year +text_seg[varIndex-2:varIndex+2]
                            if len(W2Year)>0:
                                W2YearDate, isYearFound = findYear(W2Year, isYearFound)

                    if (var11 in eachData or var12 in eachData )and (isEmployerNameFound==False) :
                        employerName=employerName+text_seg[varIndex+1:varIndex+4]
                        isEmployerNameFound=True


                    if (var21 in eachData or var22 in eachData) and (isEmployeeNameFound==False):
                        employeeName=employeeName+text_seg[varIndex+1:varIndex+4]
                        isEmployeeNameFound=True

                    if (var31 in eachData) and (isEmployerIdFound==False):
                        employerId=employerId+text_seg[varIndex+1:varIndex+4]
                        isEmployerIdFound=True

                    eachDataforWages = re.sub('[^a-z\s]+', '', eachData).strip()
                    eachDataforWages = re.sub(' +', " ", eachDataforWages)
                    if (var4 in eachDataforWages) and isWagesFound == False:
                        Wages1 = getWageData(text_seg[varIndex + 1])
                        if len(Wages1) > 0:
                            employerWages1 = Wages1
                            isWagesFound = True
                            w1p = 1
                    elif (var41 in eachDataforWages) and isWagesFound == False:
                        Wages1 = getWageData(text_seg[varIndex + 1])
                        if len(Wages1) > 0:
                            employerWages1 = Wages1
                            isWagesFound = True
                            w1p = 2


                    if (var51 in eachDataforWages) and isSSWagesFound == False:
                        Wages2 = getWageData(text_seg[varIndex + 1])
                        if len(Wages2) > 0:
                            employerWages2 = Wages2
                            isSSWagesFound = True
                    if (var61 in eachDataforWages or var62 in eachDataforWages ) and isMediWagesFound == False:
                        Wages3 = getWageData(text_seg[varIndex + 1])
                        if len(Wages3) > 0:
                            employerWages3 = Wages3
                            isMediWagesFound = True



                extracted_EmployerList=FilterData(employerName,[var11,var12])
                extracted_data["EmployerList"]=extracted_EmployerList
                extracted_data[var12]=extractEmp(extracted_EmployerList)



                extracted_EmployeeList=FilterData(employeeName,[var21,var22])
                extracted_data["EmployeeList"]=extracted_EmployeeList
                extracted_data[var22]=extractEmp(extracted_EmployeeList)

                ListEmplyerId=FilterData(employerId,[var31])
                empidList,isEmployerIdFound=getEmployerIdFirst(ListEmplyerId)
                if isEmployerIdFound==True and len(empidList)>0:
                    extracted_data[var31]=empidList[0]
                elif isEmployerIdFound2==True and len(employerId2)>0:
                    extracted_data[var31]=employerId2[0]
                else:
                    extracted_data[var31]=[]

                extracted_data[var41]=WagesFound(employerWages1)
                extracted_data[var51]=WagesFound(employerWages2)
                extracted_data[var61]=WagesFound(employerWages3)


                if len([W2YearDate])>0:
                    extracted_data["year"] = [W2YearDate]
                else:
                    extracted_data["year"]=[StatementYear2]
            except  Exception as e:
                print(e)
                print(" failed to process :"+str(pdfFolder))
                print()
                print()
                pass





        print(extracted_data)
        # header = extracted_data.keys()
        # csv_file.writerow(header.keys())

        pdfsOpCsv_file.writerow(extracted_data.values())

        opData.update(extracted_data)
    return opData


# def ExtractDataFomImages(ImgsPath):
#
#
#     ImgfileNames= glob.glob(str(ImgsPath)+"/*.jpg")+glob.glob(str(ImgsPath)+"/*.jpeg")+glob.glob(str(ImgsPath)+"/*.png")
#     for i,eachImg in enumerate(ImgfileNames):
#         opData = {}
#         extracted_data = {}
#         employerName = []
#         employeeName = []
#         employerId = []
#         WagesTips = []
#         SSwages = []
#         MediWages = []
#         W2Year = []
#
#         W2YearDate = []
#
#         isEmployerNameFound = False
#         isEmployeeNameFound = False
#         isEmployerIdFound = False
#
#         isWagesFound = False
#         isSSWagesFound = False
#         isMediWagesFound = False
#         isYearFound = False
#
#         isYearFound2 = False
#         foldername, file_extension = os.path.splitext(eachImg)
#         foldername = os.path.basename(foldername)
#
#         foldername=str(i)+"_"+foldername
#         newImgPath="ImgsPath+foldername+file_extension"
#         os.rename(eachImg,newImgPath)
#
#
#         extracted_data["file"]=foldername
#         imagefiles = Image.open(newImgPath)
#         text_seg = image_block_obj.process_image(imagefiles)
#         #print(text_seg)
#         if len(text_seg)>11 and isYearFound2==False:
#             StatementYear2,isYearFound2=findYear(text_seg[:5]+text_seg[-5:],isYearFound2)
#
#         for varIndex,eachData in enumerate(text_seg):
#
#             eachData=removePunctuation(eachData)
#             for eachW2year in TaxStatementYear:
#                 if eachW2year in eachData and isYearFound==False:
#                     W2Year = W2Year +text_seg[varIndex-4:varIndex+1]+ text_seg[varIndex+1:varIndex+4]
#                     if len(W2Year)>0:
#                         W2YearDate, isYearFound = findYear(W2Year, isYearFound)
#
#             if (var11 in eachData or var12 in eachData )and (isEmployerNameFound==False) :
#                 employerName=employerName+text_seg[varIndex+1:varIndex+4]
#                 isEmployerNameFound=True
#
#
#             if (var21 in eachData or var22 in eachData) and (isEmployeeNameFound==False):
#                 employeeName=employeeName+text_seg[varIndex+1:varIndex+4]
#                 isEmployeeNameFound=True
#
#             if (var31 in eachData) and (isEmployerIdFound==False):
#                 employerId=employerId+text_seg[varIndex+1:varIndex+3]
#                 isEmployerIdFound=True
#
#             if var4 in eachData or var41  in eachData:
#                 WagesTips=WagesTips+[text_seg[varIndex+1]]
#
#             if var5 in eachData:
#                 SSwages=SSwages+[text_seg[varIndex+1]]
#
#             if var6 in eachData:
#                 MediWages=MediWages+[text_seg[varIndex+1]]
#
#
#
#         extracted_data[var12]=FilterData(employerName,[var11,var12])
#         extracted_data[var22]=FilterData(employeeName,[var21,var22])
#
#         ListEmplyerId=FilterData(employerId,[var31])
#         extracted_data[var31],isEmployerIdFound=getEmployerIdFirst(ListEmplyerId)
#
#         WagesTipsList=FilterData(WagesTips, [var4])
#         extracted_data[var4]=getWageData(WagesTipsList)
#
#         #extracted_data[var4]=FilterData(WagesTips,[var4])
#
#         ssWagesList=FilterData(SSwages,[var5])
#         extracted_data[var5]=getWageData(ssWagesList)
#
#
#         MediWagesList=FilterData(MediWages,[var6])
#         extracted_data[var6]=getWageData(MediWagesList)
#
#
#         extracted_data["year"]=[W2YearDate]
#         extracted_data["year2"]=[StatementYear2]
#
#
#
#         print(extracted_data)
#         # header = extracted_data.keys()
#         # csv_file.writerow(header.keys())
#
#         #ImgOpCsv_file.writerow(extracted_data.values())
#
#         opData.update(extracted_data)
#
#     return opData

ConvertPdfToImgs(inputFolderPath)
opData1=ExtractDataFomConvertedImages(ConvertedImgsPath)
#opData2=ExtractDataFomImages(inputFolderPath)

print()
#print(opData)
import shutil
shutil.rmtree('../data/imgs')

pdfsOpObj.close()
#ImgsOpObj.close()





