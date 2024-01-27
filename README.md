## DASHBOARD RFID NIDEC/EMBRACO ITAIÓPOLIS
Dashboard de Linha, Posto de Trabalho e Operador. Utilizando Streamlit para publicação da solução.
   
#### 1. Prepare os arquivos para subir no GitHub

1.1 Faça o login no GitHunb e crie um novo repositório (make Public)

1.2 Suba os arquivos para o GitHub da seguinte maneira:<br>
Primeiro crie o arquivo 'requirements.txt' da seguinte maneira:<br>
> Através de um terminal, posicione-se na pasta onde estão os arquivos e digite os seguintes comandos:<br>
> pip install pipreqs <br>
> pipreqs ./ <br>

Agora suba os arquivos:
> git init <br>
> git add . <br>
> git commit -m 'first commit' <br>

Copie o link da URL do repositório criado no item 1.1<br>
> git remote add origin https://github.com/daltonhardt/Streamlit-dashboard.git <br>
> git push origin master <br>
     
#### 2. Preparar o ambiente no Streamlit para publicar o App<br>

2.1 Faça o login no Streamlit<br>
#### https://share.streamlit.io/signup

2.2 Faça o deploy da aplicação da seguinte maneira:<br>
> selecione "New App"<br>
> no campo 'Repository' entre com o caminho para o Github descrito no item 1.2 acima (sem a extensão '.git')<br>
#### 'daltonhardt/Streamlit-dashboard'
> no campo 'Main file path' entre com o nome do arquivo principal<br>
#### 'Dashboard-NIDEC-v4.py'
> clique em "Deploy"<br>

Agora é só acessar a URL:
#### https://dashboard-rfid.streamlit.app/
