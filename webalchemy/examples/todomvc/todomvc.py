from webalchemy.mvc import controller

class AppTodoMvc:

    def initialize(self, **kwargs):
        self.rdoc = kwargs['remote_document']
        self.controller = controller(self.rdoc, kwargs['main_html'])
        self.rdoc.JS('''

            // the data model

            #{self.controller.model} = {

                itemlist : JSON.parse(localStorage.getItem('webatodomvcdata')) || [],

                set_all_completed : function(comp_or_not) {

                    for (var i=0, ill=this.itemlist.length; i<ill; i++)
                        this.itemlist[i].completed = comp_or_not;
                    this.persist();
                },

                remove_completed : function() {
                    this.itemlist = this.itemlist.filter(
                        function(e) {return !e.completed}
                    );
                    this.persist();
                },

                remove_item : function(i) {
                    this.itemlist.splice(i,1);
                    this.persist();
                },

                add_item : function(txt) {
                    this.itemlist.push({
                        text:txt,
                        completed:false
                    });
                    this.persist();
                },

                toggle_item_completed : function(i, v) {
                    this.itemlist[i].completed = v;
                    this.persist();
                },

                persist : function() {
                    localStorage.setItem('webatodomvcdata', JSON.stringify(this.itemlist));
                }
            }

            // viewmodel

            #{self.controller.viewmodel} = {

                itembeingedited : null,

                new_item_keyup : function(e) {
                    if (e.keyCode == #{self.rdoc.KeyCode.ESC}) e.target.blur();
                    if (e.keyCode == #{self.rdoc.KeyCode.ENTER})
                        if (e.target.value.trim()!='') {
                            e.target.app.m.add_item(e.target.value);
                            e.target.value='';
                        }
                },

                edit_keyup : function(e, i) {
                    if (e.keyCode == #{self.rdoc.KeyCode.ESC}) this.itembeingedited = undefined;
                    if (e.keyCode != #{self.rdoc.KeyCode.ENTER}) return;
                    this.itembeingedited = undefined;
                    e.target.app.m.itemlist[i].text = e.target.value;
                    if (e.target.value.trim()=='') e.target.app.m.remove_item(i);
                    e.target.app.m.persist();
                },

                editing_item_changed : function(e, i, tothisitem) {
                    if (tothisitem) {
                        e.focus();
                        e.value=e.app.m.itemlist[i].text;
                    }
                    else
                        e.blur();
                },

                should_hide : function(e, i) {
                    return  ((e.app.m.itemlist[i].completed)&&(location.hash=='#/active'))     ||
                            ((!e.app.m.itemlist[i].completed)&&(location.hash=='#/completed'));
                },

                finish_editing : function(i) {
                    if (this.itembeingedited==i) this.itembeingedited=undefined;
                }
            }
        ''')

        self.controller.prerender = self.rdoc.jsfunction('''
            #{self.controller.model}.completed = 0;
            for (var i=0, il=#{self.controller.model}.itemlist, ill=il.length; i<ill; i++)
                if (il[i].completed) #{self.controller.model}.completed++;
            #{self.controller.model}.remaining = #{self.controller.model}.itemlist.length - #{self.controller.model}.completed;
        ''')

        self.controller.call_on_request_frame()
