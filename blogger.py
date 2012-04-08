#!/usr/bin/env python
#coding=UTF-8

##TODO:
##     Add screen detection, get geometry of the way a desktop is laid out, and have the window display somewhat unobtrusively... (negated by saving the location and restoring it)
##     
import pygtk
pygtk.require('2.0')
import gtk
import wordpresslib
import keybinder
import os

CONFIG = os.getenv("HOME")+"/.ublogger.conf"

class WordPress_Interface:

    def __init__(self):
        pass
    

    #posts topic
    #@staticmethod
    def _post(title, tags, body, category, hostinfo):
        url = 'http://' + hostinfo[2] + "/xmlrpc.php"
        wpc = wordpresslib.WordPressClient(url, hostinfo[0], hostinfo[1])
        wpc.selectBlog(0)
        post = wordpresslib.WordPressPost()
        post.title = title
        post.description = body
        post.tags = tags
        post.categories.append(category)
        try:
            idPost = wpc.newPost(post, True)
        except:
            print "Error"
            return False
        return True
        
    post = staticmethod(_post)

    def _get_categories(hostinfo):
        url = 'http://' + hostinfo[2] + "/xmlrpc.php"
        wpc = wordpresslib.WordPressClient(url, hostinfo[0], hostinfo[1])
        wpc.selectBlog(0)
        return wpc.getCategoryList()
        
    get_categories = staticmethod(_get_categories)

    #gets a list of recent posts
#    @staticmethod
    def get_recent_posts(count=5):
        pass

    #loads the data from a recent post
#    @staticmethod 
    def load_recent_post(id):
        pass

    #modifies an existing recent post
#    @staticmethod
    def update_recent_post(id,title, tags, body, hostinfo):
        pass

    #deletes a recent post
#    @staticmethod 
    def delete_recent_post(id):
        pass
    

class GTK_App:

    conf = os.getenv("HOME") + "/.ublogger.conf"

    ###SIGNAL HANDLERS###
    def _delete(self,widget,data=None):
        self._hide(widget,data)
        return True

    def _hide(self, widget, data=None):
        self.position = self.window.get_position()
        self.window.hide()
        self._update_show_menu("Show Window",self._show)
        self.is_visible = False
    
    def _exit(self, widget, data=None):
        self._write_config_file()
        #if there is text in any of the fields, make sure that the user wants to quit...
        gtk.main_quit()
        
    def _show(self, widget, data=None):
        self.window.stick()
        self.window.move(self.position[0],self.position[1])
        self.window.show_all()       
        self._update_show_menu("Hide Window",self._hide)
        self.is_visible = True

    def _key_handler(self, widget, event):
        if event.keyval == 115 and event.state & gtk.gdk.CONTROL_MASK:
            #ctrl-s
            self.title_entry.set_sensitive(False)
            self.tags_entry.set_sensitive(False)
            self.body_textview.set_sensitive(False)
            self.categories_combo.set_sensitive(False)

            self._post()

            self.title_entry.set_sensitive(True)
            self.tags_entry.set_sensitive(True)
            self.body_textview.set_sensitive(True)
            self.categories_combo.set_sensitive(True)

            return True
        elif event.keyval == 113 and event.state & gtk.gdk.MOD1_MASK:
            #alt-q
            self._exit(widget,None)
            return True
        elif event.keyval == 104 and event.state & gtk.gdk.CONTROL_MASK:
            #ctrl-h
            self._hide(widget, None)
            return True
        return False
            
    #MAIN WINDOW FUNCTIONS
    def _setup_title(self):
        #setup the title input box:
        self.title_box = gtk.HBox(homogeneous=False, spacing=0)

        #setup the text view
        self.title_entry = gtk.Entry()
        self.title_entry.set_size_request(self.window_x - 45,-1)
        self.title_entry.set_editable(True)

        #setup the frame
        self.title_label = gtk.Label("Title:")

        #show the frame and the textview
        self.title_entry.show()
        self.title_label.show()
        
        #pack it into a box and show the box
        self.title_box.pack_start(self.title_label, False, False, 5)
        self.title_box.pack_start(self.title_entry, False, False,0)
        self.title_box.show()
        
    def _setup_tags(self):
        ###setup the tags input box
        self.tags_box = gtk.HBox(homogeneous=False, spacing=0)
        
        #entry
        self.tags_entry = gtk.Entry()
        self.tags_entry.set_size_request((self.window_x / 2) - 45,-1)
        self.tags_entry.set_editable(True)
        #label
        self.tags_label = gtk.Label("Tags:")

        #show label and textview
        self.tags_entry.show()
        self.tags_label.show()

        self.categories_label = gtk.Label("Category:")
        self.categories_combo = gtk.combo_box_new_text()
        self.categories_combo.set_size_request((self.window_x / 2) - 72,-1)

        self.categories_label.show()
        self.categories_combo.show()

        #pack it into the box
        self.tags_box.pack_start(self.categories_label,False,False,5)
        self.tags_box.pack_start(self.categories_combo,False,False,0)
        self.tags_box.pack_start(self.tags_label,False,False,5)
        self.tags_box.pack_start(self.tags_entry,False,False,0)

 
        self.tags_box.show()

    def _setup_body(self):
        ###setup the body input box
        self.body_box = gtk.VBox(homogeneous=False, spacing=0)


        #textview
        self.body_textview = gtk.TextView(buffer=None)
        self.body_textview.set_size_request(self.window_x - 10,self.window_y - 108);
        self.body_textview.set_wrap_mode(gtk.WRAP_WORD)
        self.body_textview.set_editable(True)

        #label
        self.body_frame = gtk.Frame("Body")
        self.body_frame.add(self.body_textview)
        
        #button
        self.post_button = gtk.Button("Post")
        self.post_button.connect('released',lambda y: self._post())

        #show frame and text view
        self.body_frame.show()
        self.body_textview.show()
        self.post_button.show()

        #pack it into, and show the box
        self.body_box.pack_start(self.body_frame, False,False,)
        self.body_box.pack_start(self.post_button, False,False,2)
        self.body_box.show()
    
    ###MENU STUFF###

    def _popup_menu_cb(self, widget, button, time, data = None):
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, gtk.status_icon_position_menu, 3, time, self.statusIcon)

    def _update_show_menu(self, label, func):
        children = self.menu.get_children()
        for c in children:
            if children.index(c) == 0:
                self.menu.remove(c)
                break

        menuitem = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
        menuitem.set_label(label);
        menuitem.connect('activate', func, self.statusIcon)
        self.menu.prepend(menuitem)

    def toggle_window_visible(self, data=None):
        if self.is_visible == True:
            self._hide(None, None)
        else:
            self._show(None, None)

    def _statusIcon_activate(self, status_icon):
        self.toggle_window_visible()
    

    ###CONFIG FILE FUNCTIONS###
    def _set_creds(self, user, password, host):
        self.user = user
        self.password = password
        self.host = host

    def _get_creds(self):
        return (self.user, self.password, self.host)

    def _create_config(self):
        FILE = open(CONFIG,"a")
        FILE.write("pos=0,0\n")
        FILE.write("user=username\n")
        FILE.write("pass=password\n")
        FILE.write("host=hostname\n")
        FILE.write("minimized=True\n")
        FILE.close()

    def _load_config(self):
        try:
            FILE = open(CONFIG,"r")
            config_file = []
            while 1:
                line = FILE.readline()
                if not line:
                    break
                config_file.append(line)
            FILE.close()
            position = self._get_value_(config_file[self._get_index_("pos=",config_file)]).rstrip("\n")
            user = self._get_value_(config_file[self._get_index_("user=",config_file)]).rstrip("\n")
            password = self._get_value_(config_file[self._get_index_("pass=",config_file)]).rstrip("\n")
            host = self._get_value_(config_file[self._get_index_("host=",config_file)]).rstrip("\n")
            minimized = self._get_value_(config_file[self._get_index_("minimized=",config_file)]).rstrip("\n")

            self._set_creds(user, password, host)
            
            position = position.partition(",")
            
            self.position = (int(position[0]),int(position[2]))
            
            if minimized == 'True':
                self.minimized = True
            elif minimized == 'False':
                self.minimized = False
        
            self.window.set_title("μBlogger - " + user + " @ " + host)
        except IOError as e:
            self._create_config()
            self._load_config()

    def _write_config_file(self):
        self.position = self.window.get_position()
        FILE = open(CONFIG, "w")
        output = ""
        output += "pos=" + str(self.position[0]) + "," + str(self.position[1]) + "\n"
        output += "user=" + self.user + "\n"
        output += "pass=" + self.password + "\n"
        output += "host=" + self.host + "\n"
        output += "minimized=" + str(self.minimized) + "\n"
        FILE.write(output)
        FILE.close()
            
    def _get_index_(self,substring,array):
        for item in array:
            if substring in item:
                return array.index(item)


    def _get_value_(self,line):
        p = line.partition("=")
        if p[1] != "" and p[2] != "":
            return p[2]
        else:
            return -1

    ###wordpress interface functions###
    def _clear_fields(self):
        self.title_entry.set_text("")
        self.tags_entry.set_text("")
        self.body_textview.get_buffer().set_text("")
        self.window.set_focus(self.title_entry)

    def _post(self):
        title = self.title_entry.get_text()
        tags = self.tags_entry.get_text()
        
        text_buffer = self.body_textview.get_buffer()
        body = text_buffer.get_text(text_buffer.get_start_iter(),text_buffer.get_end_iter())

        category = self.categories_combo.get_active_text()

        for cat in self.categories:
            if cat.name == category:
                category = cat.id
                break

        if WordPress_Interface.post(title, tags, body, category, (self.user, self.password, self.host)):
            print "Posted successfully"
            self._clear_fields()
        else:
            print "Error posting."
    

    def _get_entries(self,n=5):
        #todo: get the n previous entries
        pass

    def _get_categories(self):
        self.categories = []
        self.categories = WordPress_Interface.get_categories((self.user, self.password, self.host))
        for cat in self.categories:
            if cat.name != "Uncategorized":
                self.categories_combo.append_text(cat.name)
        #print self.categories

    def __init__(self):
        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("μBlogger")
        self.window.set_geometry_hints(None, 480,300,480,300,0,0,0,0,1.6,1.6)
        self.window_x = self.window.get_size()[0]
        self.window_y = self.window.get_size()[1]
        self.window.connect("delete_event", self._delete)        
        #self.window.connect("key-release-event", self._key_handler)
        self.position = self.window.get_position()
        self.window.set_position(gtk.WIN_POS_NONE)
        self.window.set_keep_above(True)
        self.window.stick()
        
        #setup the notification area icon
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_from_stock(gtk.STOCK_EDIT)
        self.statusIcon.set_visible(True)
        self.statusIcon.set_tooltip("μBlogger")
        self.statusIcon.connect('activate', self._statusIcon_activate)

        self.menu = gtk.Menu()
        menuitem = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
        menuitem.set_label("Show Window");
        menuitem.connect('activate', self._show, self.statusIcon)
        self.menu.append(menuitem)
        menuitem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        menuitem.connect('activate', self._exit, self.statusIcon)
        self.menu.append(menuitem)

        self.statusIcon.connect('popup-menu', self._popup_menu_cb, self.menu)
        #window box
        self.box = gtk.VBox(homogeneous=False, spacing=0)

        self._setup_title()
        self._setup_tags()
        self._setup_body()

        self.box.pack_start(self.title_box)
        self.box.pack_start(self.tags_box)
        self.box.pack_start(self.body_box)

        # This packs the main box into the window.
        self.window.add(self.box)
       
        self.box.show()
           
        self.is_visible = False

        self._load_config()

        self._get_categories()

    def main(self, min):
        if min != True:
            self.window.show_all()
            self.window.move(self.position[0],self.position[1])
            self._update_show_menu("Hide Window",self._hide)
            self.is_visible = True
        gtk.main()

if __name__ == "__main__":
    G_T_K = GTK_App()
    G_T_K.main(G_T_K.minimized)
