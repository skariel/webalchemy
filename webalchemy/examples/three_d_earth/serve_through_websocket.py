def run():
    from webalchemy import server
    from webalchemy.examples.three_d_earth.three_d_earth import ThreeDEarth
    server.run(ThreeDEarth)

if __name__ == '__main__':
    run()
