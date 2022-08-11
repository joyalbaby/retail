import os
from flask import Flask, render_template, redirect, request
from datetime import timedelta, datetime
from azure.storage.blob import BlobServiceClient, BlobClient, AccountSasPermissions, generate_blob_sas

#Azure Blob Storage Access Key, Container and Connection string variables.
storage_account_url = os.environ.get('account')
access_key = os.environ.get('key')
storage_connection_string = os.environ.get('connection_string')
blob_service = BlobServiceClient(account_url=storage_account_url, credential=access_key)
blob_container = os.environ.get('container')
account_name = os.environ.get('acc')

app = Flask(__name__)

@app.route('/', methods=['GET'])
def upload_csv():
    '''
    This will present the webpage to upload the CSV file. 
    '''
    return render_template('retail/upload.html')


@app.route('/upload', methods=['POST'])
def view_csv():
    '''
    This will present the webpage to view the content of the uploaded CSV file.
    Here, the user can edit the content of the CSV file and save it to the Azure Blob Storage.
    '''
    file = request.files.get('file')
    header = request.form.get('header')
    filename = file.filename
    content = file.read().decode('utf-8')
    data = []
    #Formatting the csv content into row and cells to be displayed
    for row in content.split('\r\n'):
        if len(row.split(',')) > 1:
            data.append(row.split(','))
    return render_template('retail/view_csv.html',data= data,header=header,filename=filename,len=len )


@app.route('/save', methods=['POST'])
def save_csv():
    '''
    This route will save the edited CSV file to the Azure Blob Storage.
    It will then proceed to the webpage where the user can download the edited CSV file.
    '''
    filename = request.form.get('filename')
    csv = []
    for k in request.form.keys():
        if k != 'filename':
            csv.append(request.form.getlist(k))
    csv_string =''
    #The form data is collected and concated to form the csv structure and uploaded to Blob Storage. 
    for k in zip(*csv):
        csv_string+=','.join(k)+'\r\n'
    try:
        blob = BlobClient.from_connection_string(conn_str=storage_connection_string, container_name=blob_container, blob_name=filename)
        blob.upload_blob(csv_string)
    except:
        print('Exception occured')
    return render_template('retail/download_csv.html',filename= filename)
    
@app.route('/download/<filename>', methods=['GET'])
def download_csv(filename):
    '''
    This route is to provide the user the ability to download the edited file from Blob Storage.
    This will create a Shared Access Signature (SAS) with 5 minute read only access to the file
    so that it can be downloaded directly from the Azure Blob Storage.

    :param str filename:
        The file name to be downloaded from Blob Storage.

    '''
    try:
        url = f"{storage_account_url}{blob_container}/{filename}"
        sas_token = generate_blob_sas(
            account_name=account_name,
            account_key=access_key,
            container_name=blob_container,
            blob_name=filename,
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=5)
        )

        url_with_sas = f"{url}?{sas_token}"
        return redirect(url_with_sas)
    except:
        print('Exception occured')
        return 'Something went wrong.'