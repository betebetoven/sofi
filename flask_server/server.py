from ast import Sub
from flask import Flask
from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms import FileField,SubmitField
from codecs import latin_1_encode
import tabula
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import csv
import xlsxwriter
import sys, time
 
app = Flask(__name__)
CORS(app)
class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")
#Funcionamiento básico del backend, aun por arreglar
#porque debe recibir de entrada un archivo pdf y 
cont = 0
@app.route("/sofi")
def sofi():
    global cont
    cont = cont+1
    #sofi_traduce()
    return{"sofi":["aca va hoa()","me","llamo","sofi",cont]}

if __name__=="__main__":
    def progressBar(count, total, suffix=''):
	    barLength = 60
	    filledLength = int(round(barLength * count / float(total)))
	    percent = round(100.0 * count / float(total), 1)
	    bar = '=' * filledLength + '-' * (barLength - filledLength)
	    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percent, '%', suffix))
	    sys.stdout.flush()
    def hoa():
        return("probando ota vez el arumento inicial")
    def sofi_traduce():
        estados_cuentas = []
        direccion = askopenfilename()
        nombre = direccion.split('/')
        for n in range(4):
            nombre[len(nombre)-1] = nombre[len(nombre)-1][:-1]
        print(nombre[len(nombre)-1])
        tabula.convert_into(direccion, "output.txt", output_format="csv", pages='all')
        with open("output.txt", encoding = 'latin-1') as csv_file:
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
            workbook = xlsxwriter.Workbook(asksaveasfilename(initialfile=nombre[len(nombre)-1], defaultextension=".xlsx"))
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
        return
    



    app.run(debug=True)
    