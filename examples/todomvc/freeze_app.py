from webalchemy import server
from todomvc import AppTodoMvc as app

if __name__ == '__main__':
    server.generate_static(app)
