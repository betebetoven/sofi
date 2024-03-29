#from ast import Sub
#from crypt import methods
from flask import Flask, render_template, send_file
from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms import FileField,SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from codecs import latin_1_encode
import tabula
#from tkinter.filedialog import askopenfilename
#from tkinter.filedialog import asksaveasfilename
import csv
import xlsxwriter
import sys, time
import openai
import json
import html
import pandas as pd
from io import StringIO, BytesIO
from os.path import splitext
import math
#from server import app
openai.api_key = os.environ.get("OPENAI_API_KEY") 
prompt2 = "A continuacion se te presenta el fragmento de uan factura, necesito que lo traduzcas al español lo mas formal que puedas, ya que una factura es un documento legal, el fragmento es el siguiente: "#+"\""+text6+"\""
prompt3 = "Necesito que traduzcas el siguiente texto a expañol, es el fragmento de una factura: "#+"\""+text6+"\""
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'test'
app.config['UPLOAD_FOLDER'] = 'static/Files'
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")
#Funcionamiento básico del backend, aun por arreglar
#porque debe recibir de entrada un archivo pdf y 
#esto es lo nuevo que deberia de agregar
cont = 0
@app.route("/sofi", methods = ['GET',"POST"])
def sofi():
    global cont
    cont = cont+1
    form = UploadFileForm()
    dirtub = ""
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
        dirtub = os.path.abspath("static/Files/"+secure_filename(file.filename))
        time.sleep(5)
        archivo = sofi_traduce(dirtub)
        archivo2 = os.path.abspath("static/Files/"+secure_filename(archivo +".xlsx"))
        nombre = dirtub.split('/')
        for n in range(4):
            nombre[len(nombre)-1] = nombre[len(nombre)-1][:-1]
        #aca va la eliminacion de los archivos indeseados en el servidor, los xls vamos a tener que retirarlos a mano
        os.remove(f'static/Files/{secure_filename(file.filename)}')
        


        response = send_file(nombre[len(nombre)-1]+".xlsx")
        #os.remove(f'{nombre[len(nombre)-1]}.xlsx')
        return response
        
    
    return render_template('index.html', form = form)



########################################################################################################################






@app.route("/sofiai", methods = ['GET',"POST"])
def sofiai():
    
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        input_filename = file.filename
        _, file_extension = splitext(input_filename)
        file_name, _ = splitext(input_filename)
        df_list = tabula.read_pdf(file.stream, stream=True,lattice=True, pages='all', encoding='latin1')
        df_list = [df.rename(columns=lambda x: x.replace("Unnamed: ", "")) for df in df_list]
        
        new_list = []
        fulltext = ""
        text = ""
        lines = []
        for n in df_list:

            csv_stream = n.to_csv(index=False,sep='|')
            #print(csv_stream)
            lines = csv_stream.split("|")
            print("DATAFRAME------------------------\n")
            #print(csv_stream)
            
            for t in lines:
                #print('LINEA------------------------')
                #print(t)
                #print("LINEA------------------------\n")
                if t != '':
                    fulltext+=t
                    
                    fulltext+="\n-------------------\n"
                
        
        with open('prompt2.txt', 'r') as file:
            text = file.read()
        completo = ""
        newlinse = [[]]
        newlinse.append([])
        newlinse.append([])
        
        
        for t in lines:
            if t != '' and len(t) > 3:
                com = ""
                if len(t) > 200:
                    com=traduccion2(f'{text}\n{t}')
                    newlinse[2].append("traduccion2")
                    
                elif len(t) > 40:
                    com=traduccion1(f'{text}\n{t}')
                    newlinse[2].append("traduccion1")
                else:
                    com=traduccion0(f'{text}\n{t}')
                    newlinse[2].append("traduccion0")
                    
                com = com.replace('\r', '\n',)
                com = com.replace('\n', '<br>')
                com = com.replace('\r\n', '<br>')
                
                t = t.replace('\r', '\n',)
                t = t.replace('\n', '<br>')
                t = t.replace('\r\n', '<br>')
                newlinse[1].append(com)
                newlinse[0].append(t)
            
                
            
            
                    
        #print(json.dumps(newlinse, indent=4, sort_keys=True))
        df = pd.DataFrame({"strings": newlinse[0], "original": newlinse[1]})
        
        
        
        xlsx_stream = BytesIO()

        # Create ExcelWriter and write DataFrames to separate sheets
        writer = pd.ExcelWriter(xlsx_stream, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name="Sheet1")
        max_width = df["strings"].map(len).max()

# Set the width of the first column to the maximum width
        worksheet = writer.sheets["Sheet1"]
        worksheet.set_column(0, 0,  math.sqrt(max_width))
        for row in range(df.shape[0]):
            worksheet.set_row(row, math.sqrt(max_width))
        # Save and close the ExcelWriter
        #for row in range(df.shape[0]):
            #worksheet.set_wrap(row, 0, True)
        writer.save()
        writer.close()

        # Reset stream position to beginning
        xlsx_stream.seek(0)
        forhtml = newlinse
        """for row in forhtml:
            for i, item in enumerate(row):
                row[i] = '<br>'.join(item.split('\n'))
                row[i] = '<br>'.join(item.split('\r'))
                row[i] = '<br>'.join(item.split('\n\n'))"""
                
       
            
            
        df = pd.DataFrame(forhtml)
        df_transposed = df.transpose()
        
        html_table = df_transposed.to_html(escape=False)
        return render_template('indexai.html',form = form, table=html_table)
        return send_file(xlsx_stream, download_name=f'{file_name}.xlsx', as_attachment=True)
        
    
    return render_template('indexai.html', form = form)

########################################################################################################################









palabrasReservadas = {
        'Departamento 5': "Department 5",
        'Oper. Autom.': "Automatic Operation",
        'Compensacion G': "Compensation G",
        'Bca. Empresa': "Bca. Company",
        'Cob.Cta.Ajena': "External account payment",
        'Departamento 5B': "Department 5"
    }
@app.route("/prueba", methods = ['GET',"POST"])
def prueba():
    
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        input_filename = file.filename
        _, file_extension = splitext(input_filename)
        file_name, _ = splitext(input_filename)
        df_list = tabula.read_pdf(file.stream, stream=True, pages='all', encoding='latin1')
        #df = pd.concat(df_list)
        new_list = []
        for n in df_list:

            csv_stream = n.to_csv(index=False)
            #print(csv_stream)
            lines = csv_stream.split("\n")
            for i, line in enumerate(lines):
                for word, replacement in palabrasReservadas.items():
                    lines[i] = lines[i].replace(word, replacement)
            csv_stream = "\n".join(lines) 
            lines = csv_stream.split('\n')
            lines = [line.lstrip(',') for line in lines]
            csv_stream = '\n'.join(lines)
            new_list.append(csv_stream)
        

        #aca ya tenemos la lista con las palabras modificadas
        #solo queda ingresarlas en las hojas por separado en el exccel
       # Create list of DataFrames
        df_list = []
        for csv_string in new_list:
            df_list.append(pd.read_csv(StringIO(csv_string)))
        # Create BytesIO stream
        xlsx_stream = BytesIO()

        # Create ExcelWriter and write DataFrames to separate sheets
        writer = pd.ExcelWriter(xlsx_stream, engine='xlsxwriter')
        for i, df in enumerate(df_list):
            df.to_excel(writer, sheet_name=f'sheet{i+1}', index=False)

        # Save and close the ExcelWriter
        writer.save()
        writer.close()

        # Reset stream position to beginning
        xlsx_stream.seek(0)
        return send_file(xlsx_stream, download_name=f'{file_name}.xlsx', as_attachment=True)
        
    
    return render_template('index.html', form = form)
def progressBar(count, total, suffix=''):
	    barLength = 60
	    filledLength = int(round(barLength * count / float(total)))
	    percent = round(100.0 * count / float(total), 1)
	    bar = '=' * filledLength + '-' * (barLength - filledLength)
	    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percent, '%', suffix))
	    sys.stdout.flush()
def hoa():
    return("probando ota vez el arumento inicial")
def sofi_traduce(direccion):
    estados_cuentas = []
    #direccion = askopenfilename()
    nombre = direccion.split('/')
    for n in range(4):
        nombre[len(nombre)-1] = nombre[len(nombre)-1][:-1]
    print(nombre[len(nombre)-1])
    tabula.convert_into(direccion, f'{nombre[len(nombre)-1]}.txt', output_format="csv", pages='all')
    with open(f'{nombre[len(nombre)-1]}.txt', encoding = 'latin-1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        #print(csv_reader)
        my_list = []
        cont = 1
        progresocont = 0
        tot = 0
        print("Examinando PDF \n")
        for row in csv_reader:
            progressBar(progresocont,250)
            progresocont = progresocont +1
            tmp = []
            print(row)
            strmp = '|'.join(row)
            tmp = strmp.split('|')
            palabrasReservadas = {'Departamento 5': "Department 5",
            'Oper. Autom.': "Automatic Operation" ,
            'Compensacion G': "Compensation G",
            'Bca. Empresa': "Bca. Company" ,
            'Cob.Cta.Ajena':"External account payment",
            'Departamento 5B':"Department 5"
            }
            for n in tmp:
                salida = palabrasReservadas.get(n)
                if(salida != None):
                    tmp[tmp.index(n)] = salida  
            my_list.append(tmp)
        progressBar(progresocont,progresocont)     
        estados_cuentas.append(my_list)   
        #workbook = xlsxwriter.Workbook(asksaveasfilename(initialfile=nombre[len(nombre)-1], defaultextension=".xlsx"))
        workbook = xlsxwriter.Workbook(nombre[len(nombre)-1]+".xlsx")
        worksheet = workbook.add_worksheet()
        col = 0
        print("\n")
        print("ESCRIBIENDO XLCS \n")
        for row, data in enumerate(my_list):
            progressBar(row,len(my_list))
            worksheet.write_row(row, col, data)
        worksheet.write_row(len(my_list),0,"ESPACIO")
        worksheet.default_col_width = 30
        progressBar(len(my_list),len(my_list))
        print("\nREALIZACION EXITOSA") 
    workbook.close()
    os.remove(f'{nombre[len(nombre)-1]}.txt')
    return nombre[len(nombre)-1]
    
############################################

def join_lines(cell):
    return " ".join(cell.split("\n"))
def sofi_traduce2(direccion):
    estados_cuentas = []
    #direccion = askopenfilename()
    nombre = direccion.split('/')
    for n in range(4):
        nombre[len(nombre)-1] = nombre[len(nombre)-1][:-1]
    print(nombre[len(nombre)-1])
    #df = tabula.read_pdf(direccion, lattice=True, pages='all')
    df = tabula.read_pdf(direccion, pages='all', encoding='latin1')
    df = df.applymap(join_lines)
    print("ACA ESTA EL DATA FRAME")
    for n in df:
        print(n)
    
    tabula.convert_into(direccion, f'{nombre[len(nombre)-1]}.txt', output_format="csv", pages='all')
    with open(f'{nombre[len(nombre)-1]}.txt', encoding = 'latin-1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        my_list = []
        cont = 1
        progresocont = 0
        tot = 0
        print("Examinando PDF \n")
        for row in csv_reader:
            progressBar(progresocont,250)
            progresocont = progresocont +1
            tmp = []
            strmp = '|'.join(row)
            tmp = strmp.split('|')
            palabrasReservadas = {'Departamento 5': "Department 5",
            'Oper. Autom.': "Automatic Operation" ,
            'Compensacion G': "Compensation G",
            'Bca. Empresa': "Bca. Company" ,
            'Cob.Cta.Ajena':"External account payment",
            'Departamento 5B':"Department 5"
            }
            for n in tmp:
                salida = palabrasReservadas.get(n)
                if(salida != None):
                    tmp[tmp.index(n)] = salida  
            my_list.append(tmp)
        progressBar(progresocont,progresocont)     
        estados_cuentas.append(my_list)   
        #workbook = xlsxwriter.Workbook(asksaveasfilename(initialfile=nombre[len(nombre)-1], defaultextension=".xlsx"))
        workbook = xlsxwriter.Workbook(nombre[len(nombre)-1]+".xlsx")
        worksheet = workbook.add_worksheet()
        col = 0
        print("\n")
        print("ESCRIBIENDO XLCS \n")
        for row, data in enumerate(my_list):
            progressBar(row,len(my_list))
            worksheet.write_row(row, col, data)
        worksheet.write_row(len(my_list),0,"ESPACIO")
        worksheet.default_col_width = 30
        progressBar(len(my_list),len(my_list))
        print("\nREALIZACION EXITOSA") 
    workbook.close()
    os.remove(f'{nombre[len(nombre)-1]}.txt')
    return nombre[len(nombre)-1]
    
def traduccion2(texto):
    model = openai.Completion.create(
    engine="text-davinci-003",
    prompt=texto, 
    temperature=1.0, 
    max_tokens=1024, 
    top_p=1, 
    frequency_penalty=0, 
    presence_penalty=0)
    
    
    #print(model.get("choices")[0].get("text"))
    return model.get("choices")[0].get("text")
def traduccion1(texto):
    model = openai.Completion.create(
    engine="text-davinci-003",
    prompt=texto, 
    temperature=0.5, 
    max_tokens=100, 
    top_p=1, 
    frequency_penalty=0, 
    presence_penalty=0)
    
    
    
    return model.get("choices")[0].get("text")
def traduccion0(texto):
    model = openai.Completion.create(
    engine="text-davinci-003",
    prompt=texto, 
    temperature=0.2, 
    max_tokens=40, 
    top_p=1, 
    frequency_penalty=0, 
    presence_penalty=0)
    
    
    
    return model.get("choices")[0].get("text")
    
def traduccion(texto):
    
    model = openai.Completion.create(engine="text-davinci-003",
    prompt=texto, 
    temperature=0.7, 
    max_tokens=1024, 
    top_p=1, 
    frequency_penalty=0, 
    presence_penalty=0)

    # Extract the most important facts from the summary
    facts = []
    #print(model.get("choices")[0].get("text").split("\n"))
    for result in model.get("choices")[0].get("text").split("\n"):
        facts.append(result)
        #if result.startswith("- "):
            #facts.append(result[2:])

    facswell = []
    for n in facts:
        if n != "":
            ansi_string = html.unescape(n)
            facswell.append(ansi_string)


    #print(json.dumps(facswell, indent=2))
    total = ""
    for n in facswell:
        total = total + n + "\n"
    return total




    
    


if __name__=="__main__":
    print("HOLA MUNDO SI ESTA CORRIENDO")
    #export FLASK_ENV=production
    #export FLASK_APP=myapp
    #gunicorn myapp:app
    



    app.run(host='0.0.0.0')
    
