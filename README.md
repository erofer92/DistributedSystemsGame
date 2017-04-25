# DistributedSystemsGame

#### Este trabalho foi feito a partir da disciplina de Sistemas Distribuidos.
Eu fiquei com a parte do Servidor enquanto minha dupla ficou com a parte do Cliente, logo decidimos que faríamos na linguagem que fosse mais interessante para cada um. O Servidor, feito em Python 3, está disponível neste repositório, porém o Cliente, feito em C#, está disponível em [github.com/jeffsantoss/MultiplayerGamer](github.com/jeffsantoss/MultiplayerGamer).

#### Objetivo
Criar um sistema que possa fazer a interação de vários Clientes a partir de um Servidor.

#### Pontos principais:
* Criar um Servidor que possa suprir a necessidade de vários Clientes simultaneamente.
* Criar um Cliente que possa se comunicar com o Servidor.
* Disponibilizar comunicação entre Cliente-Cliente através do Servidor.
* Guardar informações dos Clientes em um Banco de Dados para manter estados do mesmo.
* Sincronizar os clientes, de forma que as informações que estão em um determinado cliente, sejam refletidas em outro cliente através de previsão de delay e timer, para que eles tenham mais sincronia nos movimentos e nos seus "relógios".

#### Características:
* O Servidor foi implementado em Python3 e o Cliente em C#.
* O Servidor foi implementado a partir das bibliotecas json, sqlite3 e socket.
* A comunicação entre Cliente e Servidor foi feita via JSON.
* A comunicação foi feita estritamente para esse jogo, significando que o servidor funciona apenas para esse determinado serviço.
* Os Clientes podem salvar seu cadastro no Banco de Dados do Servidor e fazer Login no jogo.
* O Banco de Dados utilizado foi o SQLite (foram criadas apenas 2 tabelas (user e player) e poucos Selects e Inserts, pois não era o foco do trabalho).
* O Algoritmo de Sincronização dos clientes ainda está sendo definido. Não será utilizado um relógio global. O algoritmo escolhido está dependente do funcionamento do jogo, porém ainda está sendo formulado para que seja executado com maior precisão.
