# Disciplina Tópicos Especiais em Software - (A2) Trabalho WebPython - Sistema de Gerenciamento de Tarefas Web

# Sistema de Gerenciamento de Tarefas

Um sistema de gerenciamento de tarefas desenvolvido com Flask, permitindo cadastro de usuários, criação e atribuição de tarefas, e acompanhamento do progresso através de um dashboard.

## Funcionalidades

1. **Cadastro e Autenticação de Usuários**
   - Registro de novos usuários
   - Login e logout para controle de sessão
   - Acesso individualizado às tarefas

2. **Gerenciamento de Tarefas**
   - Criar, visualizar, editar e excluir tarefas
   - Cada tarefa possui título, descrição e status
   - Possibilidade de atribuir tarefas a outros usuários

3. **Status das Tarefas**
   - As tarefas podem ter status: "pendente", "em andamento" ou "concluída"
   - Filtro de tarefas por status

4. **Dashboard**
   - Visualização de todas as tarefas do grupo e/ou pessoais
   - Contadores e estatísticas de tarefas

## Tecnologias Utilizadas

- **Backend**: Flask
- **Banco de Dados**: SQLite (via SQLAlchemy)
- **Frontend**: HTML, CSS, Bootstrap 5
- **Autenticação**: Sistema próprio de login/registro

## Configuração e Execução

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone este repositório:
   ```
   git clone <url-do-repositorio>
   cd atividade_2908
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Execute a aplicação:
   ```
   python app.py
   ```

4. Acesse no navegador:
   ```
   http://localhost:5000/
   ```

## Estrutura do Projeto

- `app.py`: Arquivo principal da aplicação Flask
- `templates/`: Diretório com todos os templates HTML
- `static/`: Arquivos estáticos (CSS, JavaScript, etc.)
- `requirements.txt`: Lista de dependências do projeto

## Uso

1. Registre-se e faça login no sistema
2. Crie novas tarefas pelo botão "Nova Tarefa"
3. Visualize e gerencie suas tarefas na página "Minhas Tarefas"
4. Acompanhe o progresso geral no Dashboard

## Observações

- O banco de dados SQLite será criado automaticamente na primeira execução
- A senha secreta da aplicação deve ser alterada em ambiente de produção
