import os
from flask import Flask, render_template, request
from azure.storage.blob import BlockBlobService
account = os.environ.get('account')
key = os.environ.get('key')
blob_service = BlockBlobService(account_name=account, account_key=key)
container = os.environ.get('container')

app = Flask(__name__)

@app.route('/', methods=['GET'])
def upload_file():
    return render_template('retail/upload.html')

@app.route('/upload', methods=['POST'])
def view_csv():
    file = request.files.get('file')
    header = request.form.get('header')
    filename = file.filename
    # try:
    #     blob_service.create_blob_from_stream(container, filename, file)
    # except Exception:
    #     print('Exception=' + Exception)
    content = file.read().decode('utf-8')
    data = []
    for row in content.split('\r\n'):
        if len(row.split(',')) > 1:
            data.append(row.split(','))
    return render_template('retail/view_csv.html',data= data,header=header,filename=filename,len=len )


@app.route('/save', methods=['POST'])
def save_csv():
    filename = request.form.get('filename')
    csv = []
    for k in request.form.keys():
        if k != 'filename':
            csv.append(request.form.getlist(k))
    csv_string =''
    for k in zip(*csv):
        csv_string+=','.join(k)+'\r\n'
    try:
        blob_client = blob_service.create_blob_from_text(container,filename,csv_string)
    except:
        print('Exception occured')
    return csv_string
    
