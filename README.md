### DASHBOARD RFID NIDEC
Dashboard de Linhas, Postos de Trabalho e Operadores.

1. Utilizando Streamlit para publicação da solução
   
2. Preparar os arquivos para subir no GitHub
2.1 Criar o arquivo 'requirements.txt'
    Posicionar-se na pasta onde estão os arquivos
    # pip install pipreqs <enter>
    # pipreqs ./ <enter>
2.1 Criar um novo repositório no GitHub (make Public)
2.2 Subir os arquivos para o Github
    Posicionar-se na pasta onde estão os arquivos
    # git init <enter>
    # git add . <enter>
    # git commit -m 'first commit'
    Copie o link da URL do repositório criado no item 2.1
    # git remote add origin https://github.com/daltonhardt/Streamlit-dashboard.git <enter>
    # git push origin master
     
3. Preparar o ambiente no Streamlit para publicar o App
3.1 acesse:  share.streamlit.io  (https://share.streamlit.io/signup)
3.2 selecione "New App"
3.3 no campo 'Repository' entre com o caminho para o Github descrito no item 2.2 acima
      'daltonhardt/Streamlit-dashboard'
3.4 no campo 'Main file path' entre com o nome do arquivo principal
      'Dashboard-NIDEC-v4.py'
3.5 clique em "Deploy"
3.6 Pronto para acessar a URL:  https://dashboard-rfid.streamlit.app/
