def run():
    from webalchemy import server
    from webalchemy.examples.todomvc.todomvc import AppTodoMvc as app
    server.run(app)

if __name__ == '__main__':
    run()



