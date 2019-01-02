#!/usr/env/python 
#-*-coding:utf-8 -*-


import datetime
import glob
from threading import Thread
import threading
import time

import requests, shutil, os.path


'''
Serviço de monitoramento de diretório para processar arquivos de textos
    diretorio monitorado = files/
    diretorio backup = backup/
    diretorio repositorio = repo/
'''


'''
#****************************************
#             FUNCOES
#****************************************
'''

def stream_file(file):
    ''' 
    Função para realizar stream do arquivo texto 
    '''
    f = open(file, 'r')
    lines = f.readlines()[-1]
    f.close()
    start_time = lines[5:28]
    end_time = lines[28:51]
    title = lines[105:138]
    duration_time = lines[183:195]
    reconcile_key = lines[278:310]
    params_post = {'start_time': start_time[11:23], 'end_time' : end_time[11:23], 'title' : title, 
                   'duration_time':duration_time, 'reconcile_key': reconcile_key}
    return params_post


def envio_corte(url, params):
    '''
    Funcao para consultar status da api
    '''
    response = requests.post(url, params)
    return response


def verifica_status(url):
    '''
    função para verificar o status do processo de corte
    '''
    
    r = requests.get(url)
    status = ''
    if r.text == 'Completed':
        status = 'Completed'
    else:
        status = 'Not Completed'
    return status


def convert_time(str_time):
    '''
    Converte uma string para datetime
    '''    
    hora, minutos, seg = str_time.split(":")
    date_time = datetime.timedelta(hours=int(hora), minutes=int(minutos), seconds=int(seg))
    return date_time

'''
#*******************************
#      VARIAVEIS GLOBAIS
#*******************************
'''
url = 'https://api.play/cut' #url exemplo sem funcionalidade
repo = 'repo/repo.txt'
backup = 'backup/'
targets = 'files/*.txt'
dirs = ['repo', 'backup','files']
 
start_time = ""
end_time = ""
title = ""
duration_time = ""
reconcile_key = ""
time_base = convert_time("00:00:30")

class Status_Service(threading.Thread):
    def __init__(self, url, intervalo_tempo):
        self.url = url
        self.intervalo_tempo = intervalo_tempo
        self.status = None
        
        threading.Thread.__init__(self)
        
    def run(self):
        threading.Thread.run(self)
        while self.status != 'Completed':
            time.sleep(self.intervalo_tempo)
            r = requests.get(self.url)
            if r.text == 'Completed':
                self.status = 'Completed'
            else:
                self.status = 'Not Completed'


'''
#*******************************
#    MONITORANDO O DIRETORIO
#*******************************
'''
class Monitor(threading.Thread):
    
    def __init__(self, path):
        self.path = path
        self.status = None
        
        threading.Thread.__init__(self)
        
    
    def run(self):
        threading.Thread.run(self)
        print('Serviço ativo!')
        
        '''Verifica a existencia dos diretorios'''
        for d in dirs:
            if os.path.exists(d) == False:
                os.mkdir(d)
                
        
        while True:
            for file in sorted(glob.iglob(self.path)):
    #         for file in sorted(glob.iglob("targets/*.txt")):
                file_repo = open(repo, 'a')
                file_name = file.split("/")[1]
                
                print('Processando arquivo: ' + file_name)
                
                lines = stream_file(file)
                start_time = lines['start_time']
                end_time = lines['end_time']
                title = lines['title']
                duration_time = lines['duration_time']
                reconcile_key = lines['reconcile_key']
                
                '''#Verifica se o arquivo não existe para gravá-lo'''
                if not os.path.isfile(backup + file_name):
                    shutil.move(file, backup)
                else:
                    os.remove(file)
                    print(' ->Erro: Arquivo ja existe no diretório de destino')
                    continue
                
                '''Preparando os dados a serem gravados'''
                str_repo = file_name + ""
                str_repo = str_repo + start_time + "" 
                str_repo = str_repo + end_time + ""
                str_repo = str_repo + title + ""
                str_repo = str_repo + duration_time + ""
                str_repo = str_repo + reconcile_key + "\n"
                
                '''#Gravando dados no repositorio'''
                file_repo.write(str_repo)
                file_repo.close()
                
                hora_i = convert_time(start_time[:8])
                hora_f = convert_time(end_time[:8])
                df = hora_f - hora_i
                
                if df > time_base:
                    print(" ->OK! Enviado para corte arquivo: " + file)
                    '''Parametros de consulta da api de corte'''
                    
                    params = {'Start Time': start_time, 'End Time' : end_time, 'file':file}
                    
                    envio_corte(url, params)
                    
                    '''
                    Verifica o status do processo de corte a cada 20 segundos
                    '''
                    status = Status_Service(url, 20)
                    status.start()
                else:
                    print(" ->Erro: Não apto para corte!")
    
    
if __name__ == '__main__':
        monitor = Monitor(targets)
        monitor.start()
    
