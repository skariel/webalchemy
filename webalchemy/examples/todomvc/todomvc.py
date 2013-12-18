class AppTodoMvc:

    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        self.e = self.rdoc.parse_elements(kwargs['main_html'])
        self.js_renderpage = self.rdoc.jsfunction('''
            #{self.e.filter_all}.classList.remove('selected');
            #{self.e.filter_active}.classList.remove('selected');
            #{self.e.filter_completed}.classList.remove('selected');
            switch (location.hash) {
                case '':
                case '#/': #{self.e.filter_all}.classList.add('selected'); break;
                case '#/active': #{self.e.filter_active}.classList.add('selected'); break;
                case '#/completed': #{self.e.filter_completed}.classList.add('selected'); break;
            }

            var list = #{self.e.todo_list};
            var total = list.children.length;
            var completed = 0;

            for (var i=0; i<total; i++) {
                var it = list.children[i];
                if (it.classList.contains('completed')) {
                    completed++;
                    it.app.completedcheckbox.checked = true;
                }
                it.style.display = '';
                if ((location.hash == '#/active') &&
                    (it.classList.contains('completed')))
                        it.style.display = 'none';
                if ((location.hash == '#/completed') &&
                    (!it.classList.contains('completed')))
                        it.style.display = 'none';
            }

            var remaining = total - completed;

            #{self.e.completed_num}.textContent = completed;
            #{self.e.todo_num}.textContent = remaining;
            if (total == 0) {
                #{self.e.footer}.style.display = 'none';
                #{self.e.main}.style.display = 'none';
            } else {
                #{self.e.footer}.style.display = '';
                #{self.e.main}.style.display = '';
            }
            if (completed == total) {
                #{self.e.toggle_all}.checked = true;
            } else {
                #{self.e.toggle_all}.checked = false;
            }
            if (completed == 0) {
                #{self.e.clear_completed}.style.display = 'none';
            } else {
                #{self.e.clear_completed}.style.display = '';
            }
            if (remaining == '1') #{self.e.item_vs_items}.textContent = 'item';
            else #{self.e.item_vs_items}.textContent = 'items';

            // drop new data to disk...
            if (total == 0) localStorage['ult'] = 0;
            if (!('ult' in localStorage))
                localStorage['ult'] = 0;

            ults_in_list = []
            for (var i=0; i<list.children.length; i++) {
                var it = list.children[i];
                if (!('ult' in it)) {
                    it.ult = localStorage['ult'];
                    localStorage['ult'] = 1+parseInt(localStorage['ult']);
                }
                localStorage[it.ult] = it.app.tasktextlabel.textContent;
                localStorage[it.ult+'_completed'] = it.classList.contains('completed');
                ults_in_list.push(it.ult);
                ults_in_list.push(it.ult+'_completed');
            }
            // delete old data from disk...
            for (var key in localStorage) {
                if (key == 'ult') continue;
                if (ults_in_list.indexOf(key)<0)
                    localStorage.removeItem(key);
            }
        ''')
        self.js_createitem = self.rdoc.jsfunction('text', self.createitem)

        # binding elements
        self.rdoc.window.events.add(hashchange=self.js_renderpage)
        self.e.new_todo.events.add(blur=self.rdoc.jsfunction('e', 'e.target.value = ""'))
        self.e.new_todo.events.add(keyup=self.rdoc.jsfunction('event', '''
            if (event.keyCode == #{self.rdoc.KeyCode.ESC}) #{self.e.new_todo}.blur();
            if (event.keyCode == #{self.rdoc.KeyCode.ENTER}) {
                #{self.js_createitem}(#{self.e.new_todo}.value);
                #{self.e.new_todo}.blur();
                #{self.js_renderpage}();
            }
        '''))
        self.rdoc.inline('current_view = "all";')
        self.e.toggle_all.events.add(click=self.rdoc.jsfunction('''
            var list = #{self.e.todo_list};
            for (var i=0; i<list.children.length; i++) {
                it = list.children[i];
                if (#{self.e.toggle_all}.checked) {
                    it.classList.add('completed');
                    it.app.completedcheckbox.checked = checked = true;
                } else {
                    it.classList.remove('completed');
                    it.app.completedcheckbox.checked = checked = false;
                }
            }
            #{self.e.toggle_all}.checked = !#{self.e.toggle_all}.checked;
            #{self.js_renderpage}();
        '''))
        self.e.clear_completed.events.add(click=self.rdoc.jsfunction('''
            var items = [];
            var list = #{self.e.todo_list};
            for (var i=0; i<list.children.length; i++)
                items.push(list.children[i]);
            for (var i=0; i<items.length; i++) {
                var it = items[i];
                if (it.classList.contains('completed'))
                    list.removeChild(it);
            }
            #{self.js_renderpage}();
        '''))

        # loading from disk...
        self.rdoc.JS('''
            var list = #{self.e.todo_list}.children;
            for (var key in localStorage) {
                if (key == 'ult') continue;
                if (key.indexOf('_')>=0) continue;
                if (['watch', 'unwatch'].indexOf(key)>=0) continue;
                // we have a real item!
                #{self.js_createitem}(localStorage[key]);
                item = list[list.length-1];
                item.app.ult = key;
                if (localStorage[key+'_completed'] == 'true')
                    item.classList.add('completed');
            }
        ''')
        self.js_renderpage()

    def createitem(self, text):
        li = self.e.todo_list.element('li')
        div = li.element('div')
        div.cls.append('view')
        completedcheckbox = div.element('input')
        li.app.completedcheckbox = completedcheckbox
        completedcheckbox.att.type = 'checkBox'
        completedcheckbox.cls.append('toggle')
        tasktextlabel = div.element('label')
        tasktextlabel.text = text
        li.app.tasktextlabel = tasktextlabel
        destroybutton = div.element('button')
        destroybutton.cls.append('destroy')
        edittaskinput = li.element('input')
        edittaskinput.cls.append('edit')
        edittaskinput.prop.value = text

        # binding events...
        completedcheckbox.events.add(click=lambda: (li.cls.toggle('completed'), self.js_renderpage())[0])
        tasktextlabel.events.add(dblclick=lambda: li.cls.append('editing'))
        tasktextlabel.events.add(dblclick=lambda: edittaskinput.cal.focus())
        edittaskinput.events.add(blur=lambda: li.cls.remove('editing'))
        destroybutton.events.add(click=lambda: (li.remove(), self.js_renderpage())[0])
        edittaskinput.events.add(keyup=self.rdoc.jsfunction('event', '''
            if (event.keyCode == #{self.rdoc.KeyCode.ESC}) #{edittaskinput}.blur();
            if (event.keyCode != #{self.rdoc.KeyCode.ENTER}) return;
            #{edittaskinput}.blur();
            #{tasktextlabel}.textContent = #{edittaskinput}.value
            #{self.js_renderpage}();
        '''))


