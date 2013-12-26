def run():
    from webalchemy import server
    from webalchemy.examples.todomvc.todomvc import AppTodoMvc as app
    server.run('127.0.0.1', 8081, app, main_html_file_path='static/template/index.html')

if __name__ == '__main__':
    run()



