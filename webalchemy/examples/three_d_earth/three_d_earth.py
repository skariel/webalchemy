
class Earth:

    def __init__(self):
        self.width = window.innerWidth
        self.height = window.innerHeight

        # Earth params
        self.radius = 0.5
        self.segments = 32
        self.rotation = 6

        self.scene = new(THREE.Scene)

        self.camera = new(THREE.PerspectiveCamera, 45, self.width / self.height, 0.01, 1000)
        self.camera.position.z = 1.5

        self.renderer = new(THREE.WebGLRenderer)
        self.renderer.setSize(self.width, self.height)

        self.scene.add(new(THREE.AmbientLight, 0x333333))

        self.light = new(THREE.DirectionalLight, 0xffffff, 1)
        self.light.position.set(5, 3, 5)
        self.scene.add(self.light)

        self.sphere = self.createSphere(self.radius, self.segments)
        self.sphere.rotation.y = self.rotation
        self.scene.add(self.sphere)

        self.clouds = self.createClouds(self.radius, self.segments)
        self.clouds.rotation.y = self.rotation
        self.scene.add(self.clouds)

        self.stars = self.createStars(90, 64)
        self.scene.add(self.stars)

        self.mx = 0
        self.my = 0
        self.mdx = 0
        self.mdy = 0
        self.angx = 0
        self.angy = 0
        self.renderer.domElement.onmouseup = self.wrap(self, self.mouseup)
        self.renderer.domElement.onmousedown = self.wrap(self, self.mousedown)

    def mousemove(self, e):
        self.mdx += e.screenX - self.mx
        self.mdy += e.screenY - self.my
        self.mx = e.screenX
        self.my = e.screenY
        console.log(self.mdx + ' '+ self.mdy)

    def mouseup(self, e):
        self.mdx = 0
        self.mdy = 0
        self.renderer.domElement.onmousemove = None

    def mousedown(self, e):
        self.mx = e.screenX
        self.my = e.screenY
        self.renderer.domElement.onmousemove = self.wrap(self, self.mousemove)

    def wrap(self, object, method):
        def wrapper():
            return method.apply(object, arguments)
        return wrapper

    def render(self):
        if Math.abs(self.mdx) > 1.1 or Math.abs(self.mdy) > 1.1:
            self.angx -= self.mdx/100
            self.angx -= self.mdx/100
            if Math.abs(self.angy + self.mdy/100) < 3.14/2:
                self.angy += self.mdy/100
            self.camera.position.x = 1.5 *Math.sin(self.angx) *Math.cos(self.angy)
            self.camera.position.z = 1.5 *Math.cos(self.angx) *Math.cos(self.angy)
            self.camera.position.y = 1.5 *Math.sin(self.angy)
            self.camera.lookAt(self.scene.position)
            self.mdx = 0
            self.mdy = 0

        self.sphere.rotation.y += 0.0005
        self.clouds.rotation.y += 0.0004
        requestAnimationFrame(self.wrap(self, self.render))
        self.renderer.render(self.scene, self.camera)


    def createSphere(self, radius, segments):
        geometry = new(THREE.SphereGeometry, radius, segments, segments)
        material = new(THREE.MeshPhongMaterial, {
                        'map':         THREE.ImageUtils.loadTexture('static/2_no_clouds_4k.jpg'),
                        'bumpMap':     THREE.ImageUtils.loadTexture('static/elev_bump_4k.jpg'),
                        'bumpScale':   0.005,
                        'specularMap': THREE.ImageUtils.loadTexture('static/water_4k.png'),
                        'specular':    new(THREE.Color, 'grey')
        })
        return new(THREE.Mesh, geometry, material)

    def createClouds(self, radius, segments):
        geometry = new(THREE.SphereGeometry, radius + 0.005, segments, segments)
        material = new(THREE.MeshPhongMaterial, {
                        'map':         THREE.ImageUtils.loadTexture('static/fair_clouds_4k.png'),
                        'transparent': true
        })
        return new(THREE.Mesh, geometry,  material)

    def createStars(self, radius, segments):
        geometry = new(THREE.SphereGeometry, radius, segments, segments)
        material = new(THREE.MeshBasicMaterial, {
                        'map':  THREE.ImageUtils.loadTexture('static/galaxy_starfield.png'),
                        'side': THREE.BackSide
        })
        return new(THREE.Mesh, geometry, material)


class ThreeDEarth:

    include = ['https://rawgithub.com/mrdoob/three.js/master/build/three.min.js']

    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        self.rdoc.body.style(
            margin=0,
            overflow='hidden',
            backgroundColor='#000'
        )
        self.earth = self.rdoc.new(Earth)
        self.rdoc.body.append(self.earth.renderer.domElement)

        self.rdoc.stylesheet.rule('a').style(color='#FFF')
        e = self.rdoc.body.element('p')
        e.prop.innerHTML = "Powered by <a href='https://github.com/skariel/webalchemy'>Webalchemy</a><br/>" +\
            "Adapted from <a href='https://github.com/turban/webgl-earth/blob/master/index.html'>this</a>"
        e.style(
            color='#FFF',
            position='absolute',
            left='10px', top='10px'
        )

        self.earth.render()



