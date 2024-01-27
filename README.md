## DASHBOARD RFID NIDEC/EMBRACO ITAIÓPOLIS
Dashboard de Linha, Posto de Trabalho e Operador.

#### 1. Utilizando Streamlit para publicação da solução
   
#### 2. Preparar os arquivos para subir no GitHub

2.1 Criar o arquivo 'requirements.txt'<br>
Posicionar-se na pasta onde estão os arquivos
> pip install pipreqs <br>
> pipreqs ./ <br>

2.1 Criar um novo repositório no GitHub (make Public)

2.2 Subir os arquivos para o Github<br>
Posicionar-se na pasta onde estão os arquivos<br>
> git init <br>
> git add . <br>
> git commit -m 'first commit' <br>

Copie o link da URL do repositório criado no item 2.1<br>
> git remote add origin https://github.com/daltonhardt/Streamlit-dashboard.git <br>
> git push origin master <br>
     
#### 3. Preparar o ambiente no Streamlit para publicar o App<br>

3.1 acesse:  share.streamlit.io  (https://share.streamlit.io/signup) <br>

3.2 selecione "New App"<br>

3.3 no campo 'Repository' entre com o caminho para o Github descrito no item 2.2 acima
#### 'daltonhardt/Streamlit-dashboard'

3.4 no campo 'Main file path' entre com o nome do arquivo principal
#### 'Dashboard-NIDEC-v4.py'

3.5 clique em "Deploy"<br>

3.6 Pronto para acessar a URL:
#### https://dashboard-rfid.streamlit.app/
