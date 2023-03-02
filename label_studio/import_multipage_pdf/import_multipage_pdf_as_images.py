import shutil
import os
import glob
import json
import pdf2image
from pdf2image import convert_from_path, convert_from_bytes

# This Python script scans a specified directory for PDF documents and converts their pages to images.
# The images are stored into their respective folders organized by the orginal PDF file name.
# Once the images are created their are uploaded to GitHub for hosting.
# A JSON file is created for each PDF file with a unique URL to each images.
# That JSON is sent to Label Studio via API in order to import the images as seperate tasks into the Project specified 
# by the Project ID

f=open("/Users/bernardlawes/Documents/_Personal/SEC/labelstudio_api_token.txt","r")
lines=f.readlines()
Auth_Token=lines[0]
f.close()

#Set Label Studio Variables
LSE_HOST = "https://app.heartex.com"                        # Domain where LS is hosted
LSE_API_Token = Auth_Token                                  # API Token
ProjectID = "22187"                                         # Project ID indicated in the URL

# Set Input Folder
folderIn = '/Users/bernardlawes/Documents/GitHub/public_data/pdf/'
PDF_Files = glob.glob(folderIn + '*.pdf')                   # Scan for PDFs in the specified folder
fileCount = len(PDF_Files)                                  # Get File Count

# Set Output Directory
folderOut = "/Users/bernardlawes/Documents/GitHub/public_data/pdf/processed/"  #Set the primary parent output directory for each processed PDF 

#Set Storage URLs
storageDomain = "https://raw.githubusercontent.com/"  # Storage domain
storageFolder = storageDomain+"lawesworks/public_data/main/pdf/processed/"    # Think of this as a Bucket where I put my PDFs
JSON_File_List = []                                   # A JSON file is created for each PDF file containing URL to each image associated with it

print("\nProcessing "+str(fileCount)+" PDF Files\n")

id = 1
for PDF_File in PDF_Files:
    
    # Determine Basename and set the Output Path
    basename = os.path.splitext(os.path.basename(PDF_File))[0]      # Basename designates the folder name used for this this PDF
    outPath = folderOut+basename                                    # Set the parent output directory images associated with this PDF
    storageURL= storageFolder + basename+"/"                        # Set the parent URL for the images asscoiated with this PDF

    # Create the Output Path if Necessary
    if not os.path.exists(outPath):                                 # If the parent ouptut directory does not exist, create it.
        os.makedirs(outPath, exist_ok=True)

    print("Processing "+str(id)+" / "+ str(fileCount)+": "+basename + " | " + storageURL)

    # Convert each PDF Page to image Data
    pages = pdf2image.convert_from_path(PDF_File,200)               # Convert all pages in the PDF to image data

    # Save each image in the collection to a separate image
    for i in range(len(pages)):
        pages[i].save(outPath+'/page'+ str(i) +'.jpeg', 'JPEG')     # Save all image Data into the ouput directory 'outPath'
        
    # Create a Python object (dictionary)       
    jsonobj = {
            "id":str(id),
            "data": {
                "images":[]
            }
                }                                                   

    # fill in image urls into the JSON Object.
    for i in range(len(pages)):
        jsonobj["data"]["images"].append({"url":storageURL+"page"+str(i)+".jpeg"})   # Add a unique URL to each image into the 'images' array

    fileJSON = folderOut+"/"+basename+".json"
    # save JSON file.  
    with open(fileJSON, "w") as outfile:
        json.dump(jsonobj, outfile)                                 # This is the JSON file that will be imported into Label Studio

    # Add newly created JSON to the 
    JSON_File_List.append(fileJSON)                                 # Add this JSON file to the JSON File Collection.  
    id +=1

print("\n")

# Upload Tasks to Label Studio Enterprise
for JSON_File in JSON_File_List:
    cmd = "curl -H 'Authorization: Token "+LSE_API_Token+"' -X POST '"+LSE_HOST+"/api/projects/"+ProjectID+"/import' -F 'file=@"+JSON_File+"'"
    import_task = os.system(cmd)                                    # Iterate through the JSON File Collection.  
                                                                    # This API Call will import each JSON file as a seperate task








