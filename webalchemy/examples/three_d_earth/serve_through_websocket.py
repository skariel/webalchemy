def run():
    from webalchemy import server
    from webalchemy.examples.three_d_earth.three_d_earth import ThreeDEarth as app
    server.run('127.0.0.1', 8081, app)

if __name__ == '__main__':
    run()



