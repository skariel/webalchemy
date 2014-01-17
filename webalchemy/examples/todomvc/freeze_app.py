if __name__ == '__main__':
    from webalchemy import server
    from webalchemy.examples.todomvc.todomvc import AppTodoMvc as app
    server.generate_static(app, writefile='todomvc.html', main_html_file_path='static/template/index.html')

