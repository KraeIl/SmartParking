# Esse arquivo guarda a classe principal do programa, que é a interface, é nessa classe que tudo é inicializado 
# e que faz a conexão da IA, do arduino e do banco de dados com a interface

#Importando dependencias
from src import banco
#from src import pyduino as ard
from tkinter import ttk, messagebox, LabelFrame, Tk, Label, Entry, END, Toplevel
import time as t
from src import camFunctions
from datetime import *
import cv2

class interface():

    #Método construtor
    def __init__(self):
        #self.ard = ard

        #Iniciando a janela principal do app
        self.app = Tk() 
        self.app.title("Estacionamento")
        self.app.geometry("340x340")
        self.app.configure(background="#dde")
        self.app.resizable(False, False)

        #quadroGrid
        self.quadroGrid= LabelFrame(self.app, text= "Carros")
        self.quadroGrid.pack(fill="both", expand="yes", padx=10, pady= 10)

        #TreeView
        self.tv = ttk.Treeview(self.quadroGrid, columns= ('placa', 'horaEnt', "tarifa"), show= 'headings')
        self.tv.column('placa', minwidth= 0, width= 70)
        self.tv.column('horaEnt', minwidth= 0, width= 115)
        self.tv.column('tarifa', minwidth= 0, width= 75)
        self.tv.heading('placa', text= 'Placa')
        self.tv.heading('horaEnt', text= 'Horário de Entrada')
        self.tv.heading('tarifa', text= 'Tarifa')
        self.tv.pack()
        self.carros_no_patio = []
        self.popularTV()

        #quadroInserir
        self.quadroInserir = LabelFrame(self.app, text= "Inserir ou dar baixa em carros")
        self.quadroInserir.pack(fill= "both", expand= "yes", padx= 10, pady= 10)

        #Labels
        self.placaLabel = Label(self.quadroInserir, text= "Placa: ", background= "#dde", foreground= "#009")
        self.placaLabel.grid(column= 0, row= 0, padx= 5, pady= 5)

        #Entryes
        self.cplaca = Entry(self.quadroInserir)
        self.cplaca.grid(column= 1, row= 0, padx= 5, pady= 5)
        self.cplaca.bind('<KeyRelease>', self.checar)
        self.cplaca.bind('<Return>', (lambda event: self.inserir()))
        self.cplaca.focus()

        #WebCam1
        self.cap1= cv2.VideoCapture(1)
        self.cancelaAberta = None
        self.camPlaca()

        # #WebCam2
        # self.cap2= cv2.VideoCapture(1)
        # self.cam1Vaga()

        # #WebCam3
        # self.cap3= cv2.VideoCapture(2)
        # self.cam2Vaga()

        #Depois de tudo inicializado atribui tudo ao loop do main
        self.app.mainloop()

    #### FUNÇÕES

    #Função da camera 1 das vagas
    def cam2Vaga(self):
        cv2image= self.cap3.read()[1]
        camFunctions.camVaga4(frame=cv2image, ard= self.ard)
        camFunctions.camVaga5(frame=cv2image, ard= self.ard)
        camFunctions.camVaga6(frame=cv2image, ard= self.ard)
        self.app.after(30, self.cam2Vaga)

    #Função da camera 1 das vagas
    def cam1Vaga(self):
        cv2image= self.cap2.read()[1]
        camFunctions.camVaga1(frame=cv2image, ard= self.ard)
        camFunctions.camVaga2(frame=cv2image, ard= self.ard)
        camFunctions.camVaga3(frame=cv2image, ard= self.ard)
        self.app.after(30, self.cam1Vaga)

    #Função da camera de reconhecimento de placa
    def camPlaca(self):
        cv2image= self.cap1.read()[1]
        camFunctions.camPlaca(frame=cv2image, interface= self)
        self.app.after(30, self.camPlaca)

    #Função para preencher a TreeView
    def preencheTV(self, carros):

        #Deleta todos os itens na treeview
        self.tv.delete(*self.tv.get_children())

        #Deleta todos os carros no pátio
        self.carros_no_patio.clear()

        #Itera cada carro do banco de dados
        for c in carros:
        #Se o carro tem horário de saida é pq não está no pátio, logo é descartado
            if c[2] != None:
                continue
            else:
                #Se o carro ainda não deu saída pega o horário atual e calcula tarifa 
                #e adiciona o carro + data de entrada e tarifa no treeview e no vetor
                e = datetime.now()
                horaSaida = "%s/%s/%s " % (e.day, e.month, e.year)
                horaSaida += "%s:%s:%s" % (e.hour, e.minute, e.second)
                tarifa = self.calcPagamento(horaEntrada=c[1], horaSaida= horaSaida)
                self.tv.insert("", "end", values= (c[0], c[1], "R$: "+str(tarifa)+",00"))
                self.carros_no_patio.append(c)

    #Função para popular a TreeView
    def popularTV(self):

        #Seleciona os carros do banco de dados por ordem de entrada
        vquery= "SELECT * FROM tb_carros order by T_HORARIOENT"
        carros= banco.dql(vquery)
        
        #Preenche a treeview com os carros
        self.preencheTV(carros)
    
    #Função para abrir a cancela
    def abrirCancela(self, cancela):

        #Confere se a cancela está fechada
        if self.cancelaAberta == None:

            #Se a cancela que irá ser fechada é a cancela 1
            if cancela == "c1":
                
                #Comando para o arduino abrir a cancela 1
                #ard.abrirCancela1()

                #Seta variável de controle da cancela que está aberta
                self.cancelaAberta = "c1"

                #Printa que a cancela foi aberta (usado para debug)
                #print("SRV1OP")

            #Se a cancela que irá ser fechada é a cancela 2
            if cancela == "c2":

                #Comando para o arduino abrir a cancela 2
                #ard.abrirCancela2()

                #Seta variável de controle da cancela que está aberta
                self.cancelaAberta = "c2"

                #Printa que a cancela foi aberta (usado para debug)
                #print("SRV2OP")

    #Função para fechar a cancela
    def fecharCancela(self):
        
        #Espera o tempo de 2 segundos para fechar a cancela
        t.sleep(2)

        #Checa qual cancela está aberta
        if self.cancelaAberta == "c1":

            #Comando para fechar a cancela 1
            #ard.fecharCancela1()

            #Seta variável de controle que nenhuma cancela está aberta 
            self.cancelaAberta = None

            #Printa que a cancela foi fechada (usado para debug)
            #print("SRV1CL")

        if self.cancelaAberta == "c2":

            #Comando para fechar a cancela 1
            #ard.fecharCancela2()

            #Seta variável de controle que nenhuma cancela está aberta
            self.cancelaAberta = None   
            
            #Printa que a cancela foi fechada (usado para debug)
            #print("SRV2CL")

    #Função inserir, que lê a placa escrita no Entry e insere ou atualiza o registro no banco de dados
    def inserir(self):

        #Verificando se todos os campos foram preenchidos
        if self.cplaca.get()== "":
            messagebox.showerror(title= "ERRO", message= "Preencha todos os campos!!")
            self.cplaca.focus()
            return

        #Pegando o horário de agora
        e = datetime.now()
        horaEnt = "%s/%s/%s " % (e.day, e.month, e.year)
        horaEnt += "%s:%s:%s" % (e.hour, e.minute, e.second)

        #Tenta Selecionar o carro do banco de dados que bate com o digitado
        try:
            #Query para selecionar o caror do banco de dados
            vquery= "SELECT * FROM tb_carros WHERE T_PLACA LIKE '%" + self.cplaca.get() + "%'"
            carros = banco.dql(vquery)

            #Atribui os valores do último registro do carro
            for carro in carros:

                #Valor da placa
                vPlaca= carro[0]

                #Valor da data de entrada
                vEntrada= carro[1]

                #Valor da data de saída
                vSaida= carro[2]
            
            #Se o carro ainda não deu saida, é um carro que está no pátio
            #logo prossegue dando saida
            if vSaida == None:

                #Chamando função saída
                self.saida(vPlaca, vEntrada)
                return

            #Se o registro que achou do banco de dados já tem saída é um carro
            #que ja veio antes no estacionamento, logo prossegue inserindo 
            #um novo registro
            else:

                #Chamando função abrir cancela e passando a cancela da entrada (pois o carro está entrando)
                self.abrirCancela("c1")

                #Query para inserir no banco de dados
                vquery= "INSERT INTO tb_carros (T_PLACA, T_HORARIOENT) VALUES ('"+self.cplaca.get().upper()+"','"+horaEnt+"')"
                
                #Executando a função dml para fazer a query
                banco.dml(vquery)

                #Atribui o valor da placa do carro que entrou para a variável de controle do camfunctions
                camFunctions.placa = vPlaca

        #Se não conseguir é porque não tem, logo é 
        #um carro que nunca veio no estacionamento antes 
        #e prossegue para inserir no banco de dados       
        except Exception as e:

            #Chamando função abrir cancela e passando a cancela da entrada (pois o carro está entrando)
            self.abrirCancela("c1")

            #Query para inserir no banco de dados
            vquery= "INSERT INTO tb_carros (T_PLACA, T_HORARIOENT) VALUES ('"+self.cplaca.get().upper()+"','"+horaEnt+"')"
            
            #Executando a função dml para fazer a query
            banco.dml(vquery)

            #Atribui o valor da placa do carro que entrou para a variável de controle do camfunctions
            camFunctions.placa = self.cplaca.get()
            
        #Funções para atualizar a treeview, deletar o conteúdo do Entry e atribuir o foco ao Entry
        self.popularTV()
        self.cplaca.delete(0, END)    
        self.cplaca.focus()

    def saida(self, vPlaca, horaEnt):

        #Pega o horário atual e transforma em string
        e = datetime.now()
        horaSaida = "%s/%s/%s " % (e.day, e.month, e.year)
        horaSaida += "%s:%s:%s" % (e.hour, e.minute, e.second)     
    
        #Tratamento de erro
        try:

            #Calcula tarifa e mostra na tela para o cliente pagar
            tarifa = self.calcPagamento(horaSaida = horaSaida, horaEntrada= horaEnt)
            messagebox.showwarning(title= "PAGAMENTO", message= "O valor ficou em R$ %s Reais" % (tarifa))

            #Atualiza o último registro do banco de dados modificando o horário de saída
            vquery= "UPDATE tb_carros SET T_HORARIOSAIDA='%s' WHERE T_PLACA= '%s' AND T_HORARIOSAIDA IS NULL" % (horaSaida, vPlaca)
            banco.dml(vquery)

            #Funções para atualizar a treeview, deletar o conteúdo do Entry e atribuir o foco ao Entry
            self.popularTV()
            self.cplaca.delete(0, END)    
            self.cplaca.focus()

            #Abre cancela 2 (pois o carro está saindo) e seta o valor da placa no camfunctions
            self.abrirCancela("c2")
            camFunctions.placa = vPlaca

        except Exception as e:
            #Erro é mostrado como uma messagebox
            print(e)
            return 
        
        return

    #Função para cálcular o pagamento
    def calcPagamento(self, horaSaida, horaEntrada):

        #Transforma hora entrada e hora saida para objeto datetime
        hE = datetime.strptime(horaEntrada, '%d/%m/%Y %H:%M:%S') 
        hS = datetime.strptime(horaSaida, '%d/%m/%Y %H:%M:%S')

        #Calcula tempo de permanencia como deltatime
        permanencia = hS - hE

        #Transforma de deltatime para datetime
        diaria = False
        mes = False

        #Descobrir se tem dia e se tiver quantos dias tem
        if permanencia.days == 0:
            tempoPermanencia = datetime.strptime(str(permanencia), '%H:%M:%S')
        if permanencia.days == 1:
            tempoPermanencia = datetime.strptime(str(permanencia), '%d day, %H:%M:%S')
            diaria = True
        if permanencia.days > 1 and permanencia.days <= 31:
            tempoPermanencia = datetime.strptime(str(permanencia), '%d days, %H:%M:%S')
            diaria = True
        if permanencia.days > 31:
            tempoPermanencia = datetime.strptime(str(permanencia), '%j days, %H:%M:%S')
            mes = True

        #Pegando o total de minutos que o carro ficou, cada caso tem um calculo diferente
        if (diaria):
            totalminutos = (tempoPermanencia.day*24*60) + (tempoPermanencia.hour*60) + tempoPermanencia.minute
        elif (mes):
            totalminutos = ((tempoPermanencia.month-1)*31*24*60) + (tempoPermanencia.day*24*60) + (tempoPermanencia.hour*60) + tempoPermanencia.minute
        else:
            totalminutos = (tempoPermanencia.hour*60) + tempoPermanencia.minute

        #Tolerancia de 5 minutos
        if totalminutos < 5:
            return 0
        
        #Primeira hora + tolerancia e valor da tarifa, no caso 6 reais primeira hora
        elif totalminutos < 65:
            return 6.00
        
        #Mais de 3 horas começa a contar como período automaticamente + tolerancia
        elif totalminutos > 185:
            #Cálculo de períodos e retorno do valor da tarifa, no caso 15 reais por período
            períodos = (totalminutos//720)
            tarifa = 15 + (períodos*15)
            return tarifa

        #Mais de uma hora e menos de 3 cálculo por hora
        else:
            #Cálculo de horas e retorno do valor da tarifa, primeira hora 6 reais + 3 reais por hora
            horas = ((totalminutos-60)//60)
            tarifa = 9+(3*horas)
            return tarifa

    #Função para checar o que está sendo digitado e manda para a função de autocompletar
    def checar(self, e):

        #Pega todos os carros do banco de dados
        vquery= "SELECT * FROM tb_carros order by T_HORARIOENT"
        carros= banco.dql(vquery)

        #Pega o que foi digitado
        digitadoP = self.cplaca.get()

        #Pega o tamanho da string que foi digitada
        tamDigitado = len(self.cplaca.get())

        #Transforma o que foi digitado em maiúsculo
        self.cplaca.delete(0, END)
        self.cplaca.insert(0, digitadoP.upper())

        #Limite de caracteres
        if tamDigitado > 7:
            messagebox.showerror("ERRO!", "Limite máximo de caracteres excedido!")
            self.cplaca.delete(7, END)

        #Confere se os 3 primeiros dígitos são letras
        if tamDigitado <= 3:
            nums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
            if e.keysym in nums:
                messagebox.showerror("ERRO!", "Caractere Inválido!")
                self.cplaca.delete(0, END)
                return

        #Confere se o quarto dígito é número
        if tamDigitado == 4:
            nums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
            if e.keysym not in nums:
                if e.keysym != "Return" and e.keysym != "BackSpace" and e.keysym != "Delete": 
                    messagebox.showerror("ERRO!", "Caractere Inválido!")
                    self.cplaca.delete(0, END)
                    return
    
        #Confere se os ultimos 2 dígitos são números
        if tamDigitado > 5:
            nums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
            if e.keysym not in nums:
                if e.keysym != "Return" and e.keysym != "BackSpace" and e.keysym != "Delete": 
                    messagebox.showerror("ERRO!", "Caractere Inválido!")
                    self.cplaca.delete(0, END)
                    return

        #Confere se o usuário usou backspace ou delete
        if e.keysym != "BackSpace" and e.keysym != "Delete":
            
            #Se o que o usuário digitou é em branco finaliza o método
            if digitadoP == '': 
                return

            #Se o usuário digitou algo adiciona carros que contém o que o usuário digitou
            else:
                dados = []
                for item in carros:
                    placa = item[0]
                    if digitadoP.lower() in placa.lower():
                        if placa not in dados:
                            dados.append(item)
        
            self.autocompletarPlaca(dados)
        else:
            if self.cplaca.get() == '':
                self.popularTV()

    #Função para autocompletar o que foi digitado
    def autocompletarPlaca(self, dados):

        #Time sleep para não atrapalhar quando estiver digitando
        t.sleep(0.1)
        
        #Preenche a treeview com os carros sugeridos
        self.preencheTV(dados)

        #Pega o valor da placa do primeiro carro sugerido
        try:
            valorPlaca = dados[0][0]
        except: 
            valorPlaca = ''

        #Pega o tamanho do que foi digitado
        tamDigitado = len(self.cplaca.get())

        #Pega o que foi digitado            
        digitado = self.cplaca.get().lower()

        #Pega a placa do primeiro carro sugerido
        placaInserir = valorPlaca.lower()
        
        #Tira o que foi digitado da placa do carro
        for char in digitado:
            placaInserir = placaInserir.replace(char, '', 1)

        #Insere o restante da placa no campo e seleciona o que foi sugerido
        self.cplaca.insert(tamDigitado, placaInserir.upper())
        self.cplaca.selection_range(tamDigitado, END)




    