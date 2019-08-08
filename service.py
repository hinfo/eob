"""Serviço de monitoramento de diretório para processar arquivos de textos
    diretorio monitorado = files/
    diretorio backup = backup/
    diretorio repositorio = repo/"""
# -*-coding:utf-8 -*-
import glob
import os.path
import shutil
import threading
import time
from datetime import datetime

import requests
from dateutil.parser import parse


def stream_file(file_to_stream):
    """Função para realizar stream do arquivo texto e retornar um dicionario"""
    file = open(file_to_stream, 'r')
    lines = file.readlines()[-1]
    file.close()
    start_time = lines[5:28]
    end_time = lines[28:51]
    title = lines[105:138]
    duration_time = lines[183:195]
    reconcile_key = lines[278:310]
    params_post = {'start_time': start_time[11:23], 'end_time': end_time[11:23],
                   'title': title,
                   'duration_time': duration_time,
                   'reconcile_key': reconcile_key}
    return params_post


def envio_corte(url, params):
    """Funcao para consultar status da api"""
    response = requests.post(url, params)
    return response


def verifica_status(url):
    """função para verificar o status do processo de corte"""

    response = requests.get(url)
    status = ""
    if response.text == 'Completed':
        status = 'Completed'
    else:
        status = 'Not Completed'
    return status


class StatusService(threading.Thread):
    """Classe com o status dos diretorios"""

    def __init__(self, url, intervalo_tempo):
        self.url = url
        self.intervalo_tempo = intervalo_tempo
        self.status = None

        threading.Thread.__init__(self)

    def run(self):
        threading.Thread.run(self)
        while self.status != 'Completed':
            time.sleep(self.intervalo_tempo)
            response = requests.get(self.url)
            if response.text == 'Completed':
                self.status = 'Completed'
            else:
                self.status = 'Not Completed'


class Monitor(threading.Thread):
    """Classe com metodos para monitorar diretorios"""
    url = 'https://api.play/cut'  # url exemplo sem funcionalidade
    repo = 'repo/repo.txt'
    backup = 'backup/'
    targets = 'files/*.txt'
    dirs = ['repo', 'backup', 'files']
    start_time = ""
    end_time = ""
    title = ""
    duration_time = ""
    reconcile_key = ""
    format_time = "%H:%m:%SS"
    time_base = parse("00:00:30")

    def __init__(self, path):
        self.path = path
        self.status = None

        threading.Thread.__init__(self)

    def run(self):
        threading.Thread.run(self)
        print('Serviço ativo!')

        # Verifica a existencia dos diretorios
        for dir_in_path in self.dirs:
            if not os.path.exists(dir_in_path):
                os.mkdir(dir_in_path)

        while True:
            for file in sorted(glob.iglob(self.path)):
                #         for file in sorted(glob.iglob("targets/*.txt")):
                file_repo = open(self.repo, 'a')
                file_name = file.split("/")[1]

                print('Processando arquivo: ' + file_name)

                lines = stream_file(file)
                start_time = lines['start_time']
                end_time = lines['end_time']
                title = lines['title']
                duration_time = lines['duration_time']
                reconcile_key = lines['reconcile_key']

                # Verifica se o arquivo não existe para gravá-lo
                if not os.path.isfile(self.backup + file_name):
                    shutil.move(file, self.backup)
                else:
                    os.remove(file)
                    print(' ->Erro: Arquivo ja existe no diretório de destino')
                    continue

                # Preparando os dados a serem gravados
                str_repo = "".join([file_name, start_time, end_time, title,
                                    duration_time, reconcile_key, "\n"])

                # Gravando dados no repositorio
                file_repo.write(str_repo)
                file_repo.close()

                hora_inicial = datetime.strptime(start_time[:8],
                                                 self.format_time)
                hora_final = datetime.strptime(end_time[:8],
                                               self.format_time)
                data_final = hora_final - hora_inicial

                if data_final > self.time_base:
                    print(" ->OK! Enviado para corte arquivo: " + file)
                    # Parametros de consulta da api de corte
                    params = {'Start Time': start_time, 'End Time': end_time,
                              'file': file}

                    envio_corte(self.url, params)

                    # Verifica o status do processo de corte a cada 20 segundos
                    status = StatusService(self.url, 20)
                    status.start()
                else:
                    print(" ->Erro: Não apto para corte!")


if __name__ == '__main__':
    TARGETS = "files/*.txt"
    MONITOR = Monitor(TARGETS)
    MONITOR.start()
