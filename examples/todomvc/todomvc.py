import sys
import os

PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from webalchemy.mvc import controller

from os.path import dirname, join, normpath
BASE_DIR = dirname(__file__)


class Item:
    def __init__(self, text):
        self.completed = False
        self.text = text


class DataModel:
    def __init__(self):
        # loading local list of todos
        self.itemlist = JSON.parse(localStorage.getItem('webatodomvcdata')) or []

    def set_all_completed(self, comp_or_not):
        for item in self.itemlist:
            item.completed = comp_or_not
        self.persist()

    def remove_completed(self):
        self.itemlist = self.itemlist.filter(lambda i:  not i.completed)
        self.persist()

    def remove_item(self, i):
        self.itemlist.splice(i, 1)
        self.persist()

    def add_item(self, txt):
        self.itemlist.push(new(Item, txt))
        self.persist()

    def toggle_item_completed(self, i, v):
        self.itemlist[i].completed = v
        self.persist()

    def persist(self):
        localStorage.setItem('webatodomvcdata', JSON.stringify(self.itemlist))

    def calc_completed_and_remaining(self):
        self.completed = 0
        for item in self.itemlist:
            if item.completed:
                self.completed += 1
        self.remaining = self.itemlist.length - self.completed


class ViewModel:
    def __init__(self):
        self.itembeingedited = None

    def new_item_keyup(self, e):
        if e.keyCode == weba.KeyCode.ESC: e.target.blur()
        if e.keyCode == weba.KeyCode.ENTER:
            if e.target.value.trim() != '':
                e.target.app.m.add_item(e.target.value)
                e.target.value = ''

    def edit_keyup(self, e, i):
        if e.keyCode == weba.KeyCode.ESC:
            self.itembeingedited = None
        if e.keyCode != weba.KeyCode.ENTER: return
        self.itembeingedited = None
        e.target.app.m.itemlist[i].text = e.target.value
        if e.target.value.trim() == '':
            e.target.app.m.remove_item(i)

    def editing_item_changed(self, e, i, tothisitem):
        if tothisitem:
            e.focus()
            e.value = e.app.m.itemlist[i].text
        else:
            e.blur()

    def should_hide(self, e, i):
        return (e.app.m.itemlist[i].completed and location.hash == '#/active') or \
           (not e.app.m.itemlist[i].completed and location.hash == '#/completed')

    def finish_editing(self, i):
        if self.itembeingedited == i:
            self.itembeingedited = None


class AppTodoMvc:

    main_html_file_path = join(BASE_DIR, 'static/template/index.html')

    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        self.datamodel = self.rdoc.new(DataModel)
        self.viewmodel = self.rdoc.new(ViewModel)
        self.rdoc.translate(Item)

        controller(self.rdoc, kwargs['main_html'], m=self.datamodel, vm=self.viewmodel,
                   prerender=self.datamodel.calc_completed_and_remaining)
