from webalchemy.mvc import controller

class AppTodoMvc:

    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        self.controller = controller(self.rdoc)
        self.controller.bind_html(kwargs['main_html'])
        self.js_renderpage = self.rdoc.jsfunction('''
            var list = #{self.controller.e.todo_list};

            #{self.controller.model}.total = list.children.length;
            #{self.controller.model}.completed = 0;
            for (var i=0; i<#{self.controller.model}.total; i++)
                if (list.children[i].classList.contains('completed')) #{self.controller.model}.completed++;

            #{self.controller.model}.remaining = #{self.controller.model}.total - #{self.controller.model}.completed;

            //////////////////////////////////////////////// STORAGE STUFF /////////////////////////////////////////////
            //
            // drop new data to disk...
//            if (#{self.controller.model}.total == 0) localStorage['ult'] = 0;
//            if (!('ult' in localStorage))
//                localStorage['ult'] = 0;
//
//            ults_in_list = []
//            for (var i=0; i<list.children.length; i++) {
//                var it = list.children[i];
//                if (!('ult' in it)) {
//                    it.ult = localStorage['ult'];
//                    localStorage['ult'] = 1+parseInt(localStorage['ult']);
//                }
//                localStorage[it.ult] = it.app.tasktextlabel.textContent;
//                localStorage[it.ult+'_completed'] = it.classList.contains('completed');
//                ults_in_list.push(it.ult);
//                ults_in_list.push(it.ult+'_completed');
//            }
//            // delete old data from disk...
//            for (var key in localStorage) {
//                if (key == 'ult') continue;
//                if (ults_in_list.indexOf(key)<0)
//                    localStorage.removeItem(key);
//            }
        ''')
        self.js_createitem = self.rdoc.jsfunction('text', self.createitem)

        # binding elements
        self.controller.e.new_todo.events.add(keyup=self.rdoc.jsfunction('event', '''
            if (event.keyCode == #{self.rdoc.KeyCode.ESC}) #{self.controller.e.new_todo}.blur();
            if (event.keyCode == #{self.rdoc.KeyCode.ENTER}) {
                if (#{self.controller.e.new_todo}.value.trim()!='')
                    #{self.js_createitem}(#{self.controller.e.new_todo}.value);
                #{self.controller.e.new_todo}.blur();
            }
        '''))
        self.controller.e.toggle_all.events.add(click=self.rdoc.jsfunction('''
            var list = #{self.controller.e.todo_list};
            for (var i=0; i<list.children.length; i++) {
                it = list.children[i];
                if (#{self.controller.e.toggle_all}.checked) {
                    it.classList.add('completed');
                } else {
                    it.classList.remove('completed');
                }
            }
        '''))
        self.controller.e.clear_completed.events.add(click=self.rdoc.jsfunction('''
            var items = [];
            var list = #{self.controller.e.todo_list};
            for (var i=0; i<list.children.length; i++)
                items.push(list.children[i]);
            for (var i=0; i<items.length; i++) {
                var it = items[i];
                if (it.classList.contains('completed'))
                    list.removeChild(it);
            }
        '''))

        # loading from disk...
        # self.rdoc.JS('''
        #     var list = #{self.controller.e.todo_list}.children;
        #     for (var key in localStorage) {
        #         if (key == 'ult') continue;
        #         if (key.indexOf('_')>=0) continue;
        #         if (['watch', 'unwatch'].indexOf(key)>=0) continue;
        #         // we have a real item!
        #         #{self.js_createitem}(localStorage[key]);
        #         item = list[list.length-1];
        #         item.app.ult = key;
        #         if (localStorage[key+'_completed'] == 'true')
        #             item.classList.add('completed');
        #     }
        # ''')

        self.rdoc.JS('''
            // some dmmy model
            #{self.controller.model}.itemlist=[
                {
                    text:'hi1',
                    completed:true
                },
                {
                    text:'hi2',
                    completed:false
                },
                {
                    text:'hi3',
                    completed:true
                }]
        ''')
        self.controller.prerender = self.js_renderpage
        self.controller.call_on_request_frame()

    def createitem(self, text):
        li = self.controller.e.todo_list.element('li', app=True)
        div = li.element('div')
        div.cls.append('view')
        completedcheckbox = div.element('input')
        completedcheckbox.att.type = 'checkBox'
        completedcheckbox.cls.append('toggle')
        tasktextlabel = div.element('label', text)
        li.app.tasktextlabel = tasktextlabel
        destroybutton = div.element('button')
        destroybutton.cls.append('destroy')
        edittaskinput = li.element('input')
        edittaskinput.cls.append('edit')
        edittaskinput.prop.value = text

        # binding events...
        completedcheckbox.events.add(click=lambda: li.cls.toggle('completed'))
        tasktextlabel.events.add(dblclick=lambda: li.cls.append('editing'))
        tasktextlabel.events.add(dblclick=lambda: edittaskinput.cal.focus())
        edittaskinput.events.add(blur=lambda: li.cls.remove('editing'))
        destroybutton.events.add(click=lambda: li.remove())
        edittaskinput.events.add(keyup=self.rdoc.jsfunction('event', '''
            if (event.keyCode == #{self.rdoc.KeyCode.ESC}) #{edittaskinput}.blur();
            if (event.keyCode != #{self.rdoc.KeyCode.ENTER}) return;
            #{edittaskinput}.blur();
            #{tasktextlabel}.textContent = #{edittaskinput}.value
            if (#{edittaskinput}.value.trim()!='') return;
            #{li}.parentNode.removeChild(#{li});
        '''))
        self.controller.bind('toggled_style', li, '''((element.classList.contains("completed"))&&(location.hash=="#/active"))||
                ((!(element.classList.contains("completed")))&&(location.hash=="#/completed"))''', '"display"', '"none"')
        self.controller.bind('property', completedcheckbox, li.varname+'.classList.contains("completed")', '"checked"');
