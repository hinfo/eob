<h1> EOB - The Eye Of Beholder </h1>
<h3>Serviço de envio para API de corte de video</h3>
<h4>Service para monitorar um diretório e realizar ações com os arquivos</h4>
<p>Neste exemplo, o service processa arquivos 'txt' e procura campos para processamento de dados utilizando threads</p>
<p></p>
<h3>Requerimentos</h3>
<ul>
	<li>Python 3.6</li>
	<li>Requests Resource</li>
</ul>

*****************
Funcionamento
*****************
- O serviço monitora arquivos no diretório "files". 
- Os arquivos inseridos neste diretório serão processados e movidos para outro diretório chamado "backup".
- Os dados processados são armazenados no arquivo "repo.txt" dentro do diretório "repo".
- Se o arquivo já foi processado anteriormente (é verificada a existência do mesmo no diretório de backup) é removido.

****************
Execução
****************
 $ python service.py
 
*********************
Obs:
********************
- Não foram executas as consultas e o envio à API de corte de video pois esta não foi implementada
- Apenas foram simulados os posts e requests a url generica do google como testes de envio de parametros.
