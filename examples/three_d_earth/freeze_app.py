if __name__ == '__main__':
    from webalchemy import server
    from webalchemy.examples.three_d_earth.three_d_earth import ThreeDEarth as app
    server.generate_static(app, writefile='webglearth.html')

