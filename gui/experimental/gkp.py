#!/usr/bin/python

# requirements
import json
from Tkinter import *
import Tkinter
from PIL import ImageTk, Image
import tkFont
from tkMessageBox import showinfo
from ttk import *
from SIBLib import *
from termcolor import *
import sys
from RDFIndicationHandler import *
from SPARQLIndicationHandler import *

# font
TITLE_FONT = ("Helvetica", 18, "bold")

general_sparql_query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://smartM3Lab/Ontology.owl#>
SELECT ?s ?p ?o
WHERE { ?s ?p ?o }"""


# main class
class Application(Tkinter.Tk):


    # Constructor
    def __init__(self, *args, **kwargs): 

        # calling the old constructor
        Tkinter.Tk.__init__(self, *args, **kwargs)

        # creating and placing a main frame
        self.container = Tkinter.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # frames
        self.frames = {}
        for F in (StartPage, SibInteraction, SibSearch):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    # This function puts on top the frame of the given class
    def show_frame(self, c):
        frame = self.frames[c]
        frame.tkraise()

        # self.s = Style()
        # self.s.theme_use('clam')
        # self.createWidgets()

        self.joined = False
        self.kp = None

        # active subscriptions
        self.container.rdf_subscriptions = {}
        self.container.sparql_subscriptions = {}
        
    # Destroyer!
    def destroy(self):
        print "Bye!"
        sys.exit()

# This is the main interface
class StartPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        
        Tkinter.Frame.__init__(self, parent) 
        label = Tkinter.Label(self, text="Welcome to the MultiSIB client", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        button1 = Tkinter.Button(self, text="Look for a SIB", 
                            command=lambda: controller.show_frame(SibSearch))
        button2 = Tkinter.Button(self, text="Connect to a known SIB",
                            command=lambda: controller.show_frame(SibInteraction))
        button1.pack()
        button2.pack()



########################################################
##
## SibSearch Class
##
########################################################

class SibSearch(Tkinter.Frame):

    # connect method
    def connect(self):

        # get the list of selected SIBs
        # if there is only one SIB selected, then recall the other frame
        # otherwise request the creation of a multisib, and then call the other frame


    # reload method

    # quit method
    def destroy(self):
        sys.exit()

    # constructor
    def __init__(self, parent, controller):

        # Tkinter.Frame constructor
        Tkinter.Frame.__init__(self, parent) 

        # Discovery message
        discovery_msg = {"command":"DiscoveryAll"}

        # Manager instance
        manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        manager_socket.connect(("10.143.250.58", 17714))
        manager_socket.send(json.dumps(discovery_msg))

        # wait for a reply from the manager
        while 1:

            # receive a message
            msg = manager_socket.recv(4096)
            if msg:
                print colored("client_process> ", "blue", attrs=["bold"]) + 'Received the following message:'
                print msg
                manager_socket.close()
                break

        # parsing the reply
        parsed_msg = json.loads(msg)
        
        # the reply contains a failure
        if parsed_msg["return"] == "fail":
            print colored("client_process> ", "red", attrs=["bold"]) + 'Request failed!' + parsed_msg["cause"]
            
        # the reply represents a success
        elif parsed_msg["return"] == "ok":
            virtual_sib_list = parsed_msg["virtual_sib_list"]

            i = 1
            vsib = []
            for vs in virtual_sib_list:
                sib_info = "[" + str(i) + "] sib_id: " + vs + " (ip: " + virtual_sib_list[vs]['ip'] + ", port: " + virtual_sib_list[vs]['port'] + ")" 
                vsib.append(sib_info)
                i += 1

        # Sib Selection Label
        self.sib_selection_label = Label(self, text = "Select one or more SIB to connect to:")
        self.sib_selection_label.grid(row = 0, column = 0, padx = 30, pady = 10, sticky = E + W)
        
        # Sib Selection ListBox
        self.sib_selection_listbox = Listbox(self)
        self.sib_selection_listbox.config(selectmode = MULTIPLE, width = 150)    
        i = 0
        for s in vsib:
            i += 1
            self.sib_selection_listbox.insert(i, s)
        self.sib_selection_listbox.grid(row = 1, column = 0, padx = 30, pady = 10, sticky = E + W)

        # Buttons Frame
        self.buttons_frame = Frame(self)
        self.buttons_frame.grid(row = 2, column = 0)

        # Back Button
        self.back_button = Tkinter.Button(self.buttons_frame, text="Back", command=lambda: controller.show_frame(StartPage))
        self.back_button.pack(side = LEFT)

        # Connect Button
        self.connect_button = Tkinter.Button(self.buttons_frame, text="Connect")
        self.connect_button.pack(side = LEFT)
        self.connect_button["command"] = self.connect

        # Refresh Button
        self.refresh_button = Tkinter.Button(self.buttons_frame, text="Refresh")
        self.refresh_button.pack(side = LEFT)

        # Quit button
        self.quit_button = Tkinter.Button(self.buttons_frame, text="Quit")
        self.quit_button["command"] = self.destroy
        self.quit_button.pack(side = LEFT)



########################################################
##
## SibInteraction Class
##
########################################################

class SibInteraction(Tkinter.Frame):

    ########################################################
    ##
    ## JOIN or LEAVE
    ##
    ########################################################
    
    # Join/Leave method
    def joinleave(self):

        if self.joined:

            print "Leave request:",

            # disable all the buttons
            self.insert_button.config(state = DISABLED)
            self.remove_button.config(state = DISABLED)
            self.rdf_query_button.config(state = DISABLED)
            self.rdf_query_all_button.config(state = DISABLED)
            self.rdf_subscription_button.config(state = DISABLED)
            self.rdf_unsubscription_button.config(state = DISABLED)
            self.sparql_query_button.config(state = DISABLED)
            self.sparql_query_all_button.config(state = DISABLED)
            self.sparql_subscription_button.config(state = DISABLED)
            self.sparql_unsubscription_button.config(state = DISABLED)
            self.joinleave_button["text"] = "Join"
            self.joined = False

            try: 
                self.kp.leave_sib()
                
                # notify the join success
                self.notification_label["text"] = 'Leaved succesfully!'
                print "OK!"

            except:
                
                # notify the failure
                self.notification_label["text"] = 'Error while leaving the SIB'
                print colored("failed!", "red", attrs=["bold"])

                # re-enable the connection fields
                self.sib_address_entry.config(state = NORMAL)
                self.sib_port_entry.config(state = NORMAL)

            # forget about the joined sib
            self.kp = None

            # re-enable connection fields
            self.sib_address_entry.config(state = NORMAL)
            self.sib_port_entry.config(state = NORMAL)

            # disable rdf/sparql entries
            self.sparql_text.config(state = DISABLED)
            self.subject_entry.config(state = DISABLED)
            self.predicate_entry.config(state = DISABLED)
            self.object_entry.config(state = DISABLED)

        else:

            print "Join request:",
            
            # get sib ip and port
            sib_ip = self.sib_address_entry.get()
            sib_port = int(self.sib_port_entry.get())
            
            # create a SIBLib instance
            try:
                self.kp = SibLib(sib_ip, sib_port)
                self.joined = True
                self.joinleave_button["text"] = "Leave"

                # enable all the buttons
                self.insert_button.config(state = NORMAL)
                self.remove_button.config(state = NORMAL)
                self.rdf_query_button.config(state = NORMAL)
                self.rdf_query_all_button.config(state = NORMAL)
                self.rdf_subscription_button.config(state = NORMAL)
                self.rdf_unsubscription_button.config(state = NORMAL)
                self.sparql_query_button.config(state = NORMAL)
                self.sparql_query_all_button.config(state = NORMAL)
                self.sparql_subscription_button.config(state = NORMAL)
                self.sparql_unsubscription_button.config(state = NORMAL)

                # disable connection fields
                self.sib_address_entry.config(state = DISABLED)
                self.sib_port_entry.config(state = DISABLED)

                # enable rdf/sparql entries
                self.sparql_text.config(state = NORMAL)
                self.subject_entry.config(state = NORMAL)
                self.predicate_entry.config(state = NORMAL)
                self.object_entry.config(state = NORMAL)                
                self.sparql_text.delete(1.0, END)
                self.sparql_text.insert(INSERT, general_sparql_query)

                # notify the join success
                self.notification_label["text"] = 'Joined succesfully!'
                print "OK!"

            except:
                self.notification_label["text"] = 'Error while joining the SIB'
                print colored("failed!", "red", attrs=["bold"])

    ########################################################
    ##
    ## RDF QUERY
    ##
    ########################################################

    def rdf_query(self):
        
        # get the subject
        s = self.subject_entry.get()
        subj = None if s == "*" else URI(s)

        # get the predicate
        p = self.predicate_entry.get()
        pred = None if p == "*" else URI(p)

        # get the object
        o = self.object_entry.get()
        obj = None if o == "*" else URI(o)

        # build the Triple object
        t = Triple(subj, pred, obj)
        print "RDF Query to " + str(t) + ":",

        # query
        try:
            res = self.kp.execute_rdf_query(t)
            s = ""
            s = str(len(res)) + " Triples\n"
            for t in res:
                s = s + str(t[0]) + " " + str(t[1]) + " " + str(t[2]) + "\n"
            
            # update the result field
            self.results_text.config(state = NORMAL)
            self.results_text.delete(1.0, END)
            self.results_text.insert(INSERT, s)
            self.results_text.config(state = DISABLED)

            # notify the success
            self.notification_label["text"] = 'RDF query succesful!'
            print "OK!"

        except:

            # notify the failure
            self.notification_label["text"] = 'Error while querying the SIB'
            print colored("failed!", "red", attrs=["bold"])
            print sys.exc_info()


    ########################################################
    ##
    ## RDF QUERY ALL
    ##
    ########################################################

    def rdf_query_all(self):
        
        # build the Triple object
        t = Triple(None, None, None)
        print "RDF Query to " + str(t) + ":",

        # query
        try:
            res = self.kp.execute_rdf_query(t)
            s = ""
            s = str(len(res)) + " Triples\n"
            for t in res:
                s = s + str(t[0]) + " " + str(t[1]) + " " + str(t[2]) + "\n"
            
            # update the result field
            self.results_text.config(state = NORMAL)
            self.results_text.delete(1.0, END)
            self.results_text.insert(INSERT, s)
            self.results_text.config(state = DISABLED)

            # notify the success
            self.notification_label["text"] = 'RDF query succesful!'
            print "OK!"

        except:

            # notify the failure
            self.notification_label["text"] = 'Error while querying the SIB'
            print colored("failed!", "red", attrs=["bold"])
            print sys.exc_info()


    ########################################################
    ##
    ## INSERT
    ##
    ########################################################

    def insert(self):
        
        # get the subject
        subj = URI(self.subject_entry.get())

        # get the predicate
        pred = URI(self.predicate_entry.get())

        # get the object
        obj = URI(self.object_entry.get())

        # build the triple
        t = Triple(subj, pred, obj)

        # notification
        print "Insert request for triple " + str(t) + ":",

        try:
            # insert the triple
            self.kp.insert(t)

            # notification
            self.notification_label["text"] = 'RDF insert succesful'
            print "OK!"

        except:

            # failure notification
            self.notification_label["text"] = 'Error inserting a triple into the SIB'
            print colored("failed!", "red", attrs=["bold"])
            print sys.exc_info()


    ########################################################
    ##
    ## REMOVE
    ##
    ########################################################

    def remove(self):

        # get the subject
        s = self.subject_entry.get()
        subj = None if s == "*" else URI(s)

        # get the predicate
        p = self.predicate_entry.get()
        pred = None if p == "*" else URI(p)

        # get the object
        o = self.object_entry.get()
        obj = None if o == "*" else URI(o)

        # build the triple
        t = Triple(subj, pred, obj)

        # notification
        print "Remove request for triple " + str(t) + ":",

        try:
            # remove the triple
            self.kp.remove(t)

            # notification
            self.notification_label["text"] = 'RDF remove succesful'
            print "OK!"

        except:
            
            # failure notification
            self.notification_label["text"] = 'Error removing a triple from the SIB'
            print colored("failed!", "red", attrs=["bold"])
            print sys.exc_info()                  


    ########################################################
    ##
    ## RDF SUBSCRIPTION
    ##
    ########################################################

    def rdf_subscription(self):

        # get the subject
        s = self.subject_entry.get()
        subj = None if s == "*" else URI(s)

        # get the predicate
        p = self.predicate_entry.get()
        pred = None if p == "*" else URI(p)

        # get the object
        o = self.object_entry.get()
        obj = None if o == "*" else URI(o)

        # build the triple
        t = Triple(subj, pred, obj)

        # notification
        print "RDF Subscription to " + str(t) + ":",
        
        # subscribe
        try:
            s = self.kp.create_rdf_subscription(t, RDFIndicationHandler(self))

            # add the subscription to the combobox
            self.rdf_active_subs_combobox.config(state = NORMAL)
            m = self.rdf_active_subs_combobox['menu']
            m.add_command(label = str(s.sub_id), command=Tkinter._setit(self.rdf_active_subs_combobox_var, str(s.sub_id)))
            self.rdf_subscriptions[s.sub_id] = s
            self.rdf_active_subs_label["text"] = "RDF Active subs (" + str(len(self.rdf_subscriptions)) + ")"

            # initial results
            ir = self.kp.rdf_initial_results()

            # enable and clear the text area
            self.results_text.config(state = NORMAL)
            self.results_text.delete(1.0, END)
        
            # notify the initial results
            self.results_text.insert(INSERT, "Initial results:\n")
            i = ""
            for t in ir:
                i = i + str(t[0]) + " " + str(t[1]) + " " + str(t[2]) + "\n" 
            self.results_text.insert(INSERT, i + "\n")

            # disable the text area
            self.results_text.config(state = DISABLED)            

            # notification
            print "OK!"
            self.notification_label["text"] = 'Subscribe request successful!'

        except:
            
            # notify the failure
            self.notification_label["text"] = 'Error during Subscription'
            print colored("failed!", "red", attrs=["bold"])
            print sys.exc_info()
            

    ########################################################
    ##
    ## RDF UNSUBSCRIBE
    ##
    ########################################################
    
    def rdf_unsubscription(self):
        
        # get the subscription id      
        sub_id = self.rdf_active_subs_combobox_var.get()

        # notification
        print "Unsubscribe request for " + str(sub_id) + ":",

        try:
            
            # unsubscribe
            self.kp.unsubscribe(self.rdf_subscriptions[sub_id])

            # remove the subscription from the dictionary
            del self.rdf_subscriptions[sub_id]

            # remove the subscription from the combobox
            self.rdf_active_subs_combobox.config(state = NORMAL)
            m = self.rdf_active_subs_combobox['menu']
            m.delete(0, 'end')
            for sub in self.rdf_subscriptions.keys():
                m.add_command(label = str(sub), command=Tkinter._setit(self.rdf_active_subs_combobox_var, str(sub)))            
            self.rdf_active_subs_combobox_var.set('')
            self.rdf_active_subs_label["text"] = "RDF Active subs (" + str(len(self.rdf_subscriptions)) + ")"

            # enable and clear the text area
            self.results_text.config(state = NORMAL)
            self.results_text.delete(1.0, END)

            # disable the text area
            self.results_text.config(state = DISABLED)            

            # notification
            print "OK"
            self.notification_label["text"] = 'Unsubscribe request successful!'

        except:

            # notification of the failure
            self.notification_label["text"] = 'Unsubscribe request failed!'
            print colored("failed!", "red", attrs=["bold"])
            print sys.exc_info()


    ########################################################
    ##
    ## SPARQL QUERY
    ##
    ########################################################

    def sparql_query(self):
        
        # get the sparql query
        q = self.sparql_text.get(1.0, END)
        cmd = q.split()[0]

        # notification
        print "SPARQL query: ",
        
        # execute the query
        try:
            res = self.kp.execute_sparql_query(q)

            if cmd == "SELECT":
                # s = ""
                # for t in res:
                #     s = s + str(t[0][2]) + " " + str(t[1][2]) + " " + str(t[2][2]) + "\n"
                s = str(res)
                
                # update the result field
                self.results_text.config(state = NORMAL)
                self.results_text.delete(1.0, END)
                self.results_text.insert(INSERT, s)
                self.results_text.config(state = DISABLED)

            # notification
            self.notification_label["text"] = 'SPARQL ' + cmd.lower() + ' succesful'
            print "OK!"

        except:

            # notify the failure
            self.notification_label["text"] = 'Error with SPARQL ' + cmd.lower()
            print colored("failed!", "red", attrs=["bold"])
            print sys.exc_info()
        

    ########################################################
    ##
    ## SPARQL QUERY ALL
    ##
    ########################################################

    def sparql_query_all(self):
        
        # get the sparql query
        q = """SELECT ?s ?p ?o WHERE { ?s ?p ?o }"""
        print "SPARQL query: ",
        
        # execute the query
        try:
            res = self.kp.execute_sparql_query(q)

            s = ""
            for t in res:
                s = s + str(t[0][2]) + " " + str(t[1][2]) + " " + str(t[2][2]) + "\n"
                
            # update the result field
            self.results_text.config(state = NORMAL)
            self.results_text.delete(1.0, END)
            self.results_text.insert(INSERT, s)
            self.results_text.config(state = DISABLED)

            # notification
            self.notification_label["text"] = 'SPARQL query succesful'
            print "OK!"

        except:
            
            # notify the failure
            self.notification_label["text"] = 'Error with SPARQL query'
            print colored("failed!", "red", attrs=["bold"])
            print sys.exc_info()


    ########################################################
    ##
    ## SPARQL SUBSCRIPTION
    ##
    ########################################################

    def sparql_subscription(self):

        # notification
        print "SPARQL Subscription:",
        
        # get the subscription text
        s = self.sparql_text.get(1.0, END)
        
        # subscribe
        try:
            s = self.kp.create_sparql_subscription(s, SPARQLIndicationHandler(self))

            # add the subscription to the combobox
            self.sparql_active_subs_combobox.config(state = NORMAL)
            m = self.sparql_active_subs_combobox['menu']
            m.add_command(label = str(s.sub_id), command=Tkinter._setit(self.sparql_active_subs_combobox_var, str(s.sub_id)))
            self.sparql_subscriptions[s.sub_id] = s
            self.sparql_active_subs_label["text"] = "SPARQL Active subs (" + str(len(self.sparql_subscriptions)) + ")"

            # initial results
            ir = self.kp.sparql_initial_results()

            # enable and clear the text area
            self.results_text.config(state = NORMAL)
            self.results_text.delete(1.0, END)
        
            # notify the initial results
            self.results_text.insert(INSERT, "Initial results:\n")
            i = ""
            for t in ir:
                i = i + str(t[0][2]) + " " + str(t[1][2]) + " " + str(t[2][2]) + "\n" 
            self.results_text.insert(INSERT, i + "\n")

            # disable the text area
            self.results_text.config(state = DISABLED)            

            # notification
            print "OK!"
            self.notification_label["text"] = 'Subscribe request successful!'

        except:
            
            # notify the failure
            self.notification_label["text"] = 'Error during Subscription'
            print colored("failed!", "red", attrs=["bold"])
            print sys.exc_info()
            

    ########################################################
    ##
    ## SPARQL UNSUBSCRIBE
    ##
    ########################################################
    
    def sparql_unsubscription(self):
        
        # get the subscription id      
        sub_id = self.sparql_active_subs_combobox_var.get()

        # notification
        print "Unsubscribe request for " + str(sub_id) + ":",

        try:
            
            # unsubscribe
            self.kp.unsubscribe(self.sparql_subscriptions[sub_id])

            # remove the subscription from the dictionary
            del self.sparql_subscriptions[sub_id]

            # remove the subscription from the combobox
            self.sparql_active_subs_combobox.config(state = NORMAL)
            m = self.sparql_active_subs_combobox['menu']
            m.delete(0, 'end')
            for sub in self.sparql_subscriptions.keys():
                m.add_command(label = str(sub), command=Tkinter._setit(self.sparql_active_subs_combobox_var, str(sub)))            
            self.sparql_active_subs_combobox_var.set('')
            self.sparql_active_subs_label["text"] = "SPARQL Active subs (" + str(len(self.sparql_subscriptions)) + ")"

            # enable and clear the text area
            self.results_text.config(state = NORMAL)
            self.results_text.delete(1.0, END)

            # disable the text area
            self.results_text.config(state = DISABLED)            

            # notification
            print "OK"
            self.notification_label["text"] = 'Unsubscribe request successful!'

        except:

            # notification of the failure
            self.notification_label["text"] = 'Unsubscribe request failed!'
            print colored("failed!", "red", attrs=["bold"])
            print sys.exc_info()


    ########################################################
    ##
    ## INIT
    ##
    ########################################################

    def __init__(self, parent, controller):

        # Frame
        Tkinter.Frame.__init__(self, parent) 

        # attributes
        self.joined = False
        self.kp = None
        self.rdf_subscriptions = {}
        self.sparql_subscriptions = {}

        # Font
        section_font = tkFont.Font(family="Helvetica", size=14, weight="bold")

        # Connection frame
        self.connection_frame = Frame(self)
        self.connection_frame.pack() #padx = 10, pady = 10)

        # Sib address Label
        self.sib_address = Label(self.connection_frame, text="Sib address:")
        self.sib_address.pack(side = LEFT)

        # Sib address Entry
        self.sib_address_entry = Entry(self.connection_frame)
        self.sib_address_entry.pack(side = LEFT)
        self.sib_address_entry.insert(0, "127.0.0.1")

        # Sib port label
        self.sib_port = Label(self.connection_frame, text="Sib port:")
        self.sib_port.pack(side = LEFT)

        # Sib port Entry
        self.sib_port_entry = Entry(self.connection_frame)
        self.sib_port_entry.pack(side = LEFT)
        self.sib_port_entry.insert(0, "10010")

        # Join/Leave Button
        self.joinleave_button = Button(self.connection_frame)
        self.joinleave_button["text"] = "Join"
        self.joinleave_button["command"] =  self.joinleave
        self.joinleave_button.config( state = NORMAL )
        self.joinleave_button.pack( side = LEFT)        

        # Results frame
        self.results_frame = Frame(self)
        self.results_frame.pack(padx = 10, pady = 10)
        
        # Results Scrollbar
        self.results_scrollbar = Scrollbar(self.results_frame)
        self.results_scrollbar.pack(side = RIGHT, fill = Y)

        # Result Text
        self.results_text = Text(self.results_frame, yscrollcommand=self.results_scrollbar.set)
        self.results_text.pack()
        self.results_text.config(state = DISABLED)
        self.results_text.config(height = 19, width=200)
        self.results_scrollbar.config( command = self.results_text.yview )

        # RDFSPARQL frame
        self.rdfsparql_frame = Frame(self)
        self.rdfsparql_frame.pack(padx = 10, pady = 10)
        
        # RDF Label
        self.rdf_label = Label(self.rdfsparql_frame, text="RDF Interaction", font = section_font)
        self.rdf_label.grid( row = 0, sticky = NW, columnspan = 3, padx = 20, pady = 3)
        
        # Subject Label
        self.subject_label = Label(self.rdfsparql_frame, text="Subject")
        self.subject_label.grid(row = 1, column = 0, sticky = SW, padx = 20, pady = 3)

        # Subject Entry
        self.subject_entry = Entry(self.rdfsparql_frame)
        self.subject_entry.grid(row = 2, column = 0, sticky = W+N+E, padx = 20, pady = 3)
        self.subject_entry.insert(0, "http://ns#")
        self.subject_entry.config(state = DISABLED)

        # Predicate Label
        self.predicate_label = Label(self.rdfsparql_frame, text="Predicate")
        self.predicate_label.grid(row = 1, column = 1, sticky = SW, padx = 20, pady = 3)

        # Predicate Entry
        self.predicate_entry = Entry(self.rdfsparql_frame)
        self.predicate_entry.grid(row = 2, column = 1, sticky = W+E+N, padx = 20, pady = 3)
        self.predicate_entry.insert(0, "http://ns#")
        self.predicate_entry.config(state = DISABLED)

        # Object Label
        self.object_label = Label(self.rdfsparql_frame, text="Object")
        self.object_label.grid(row = 1, column = 2, sticky = SW, padx = 20, pady = 3)

        # Object Entry
        self.object_entry = Entry(self.rdfsparql_frame)
        self.object_entry.grid(row = 2, column = 2, sticky = W+E+N, padx = 20, pady = 3)
        self.object_entry.insert(0, "http://ns#")
        self.object_entry.config(state = DISABLED)

        # Buttons' Frame
        self.rdfbuttons_frame = Frame(self.rdfsparql_frame)
        self.rdfbuttons_frame.grid(row = 3, column = 0, columnspan = 3, padx = 20, pady = 3)

        # Insert button
        self.insert_button = Button(self.rdfbuttons_frame)
        self.insert_button["text"] = "Insert"
        self.insert_button["command"] =  self.insert
        self.insert_button.config( state = DISABLED )
        self.insert_button.grid(row = 0, column = 0)
        
        # Remove button
        self.remove_button = Button(self.rdfbuttons_frame)
        self.remove_button["text"] = "Remove"
        self.remove_button["command"] =  self.remove
        self.remove_button.config( state = DISABLED )
        self.remove_button.grid(row = 0, column = 1)

        # RDF query button
        self.rdf_query_button = Button(self.rdfbuttons_frame)
        self.rdf_query_button["text"] = "RDF Query"
        self.rdf_query_button["command"] =  self.rdf_query
        self.rdf_query_button.config( state = DISABLED )
        self.rdf_query_button.grid(row = 0, column = 2)

        # RDF query all button
        self.rdf_query_all_button = Button(self.rdfbuttons_frame)
        self.rdf_query_all_button["text"] = "RDF Query *"
        self.rdf_query_all_button["command"] = self.rdf_query_all
        self.rdf_query_all_button.config( state = DISABLED )
        self.rdf_query_all_button.grid(row = 0, column = 3)

        # RDF subscription button
        self.rdf_subscription_button = Button(self.rdfbuttons_frame)
        self.rdf_subscription_button["text"] = "RDF Subscription"
        self.rdf_subscription_button["command"] =  self.rdf_subscription
        self.rdf_subscription_button.config( state = DISABLED )
        self.rdf_subscription_button.grid(row = 0, column = 4)

        # Rdf_Active_Subs_Label Label
        self.rdf_active_subs_label = Label(self.rdfsparql_frame, text="RDF Active subs (0)")
        self.rdf_active_subs_label.grid(row = 4, column = 0)

        # RDF active subscriptions combobox
        self.rdf_active_subs_combobox_var = StringVar(self.rdfsparql_frame)
        self.rdf_active_subs_combobox_items = ()
        self.rdf_active_subs_combobox = OptionMenu(self.rdfsparql_frame, self.rdf_active_subs_combobox_var, self.rdf_active_subs_combobox_items)
        self.rdf_active_subs_combobox.config( state = DISABLED, width = 20 )
        self.rdf_active_subs_combobox.grid(row = 4, column = 1)

        # Rdf_Unsubscription button
        self.rdf_unsubscription_button = Button(self.rdfsparql_frame)
        self.rdf_unsubscription_button["text"] = "RDF Unsubscription"
        self.rdf_unsubscription_button["command"] =  self.rdf_unsubscription
        self.rdf_unsubscription_button.config( state = DISABLED )
        self.rdf_unsubscription_button.grid(row = 4, column = 2)
        
        # Separator
        self.sep = Frame(self.rdfsparql_frame, height = 250, relief=SUNKEN)
        self.sep.grid(row = 0, column = 3, rowspan = 5)

        # SPARQL Label
        self.sparql_label = Label(self.rdfsparql_frame, text="SPARQL Interaction", font = section_font)
        self.sparql_label.grid(row = 0, column = 4, sticky = NW, padx = 20, pady = 3)

        # Sparql Text
        self.sparql_text = Text(self.rdfsparql_frame)
        self.sparql_text.grid(row = 1, column = 4, rowspan = 2, padx = (20,0), pady = 3, columnspan = 3)
        self.sparql_text.config(height = 8, state = DISABLED)
        self.sparql_text.insert(INSERT, general_sparql_query)

        # Sparql scrollbar
        self.sparql_scrollbar = Scrollbar(self.rdfsparql_frame)
        self.sparql_scrollbar.grid(row = 1, column = 7, rowspan = 2, sticky = N + S, pady = 3, padx = (0,20))
        self.sparql_scrollbar.config( command = self.sparql_text.yview )
        self.sparql_text.config(yscrollcommand=self.sparql_scrollbar.set)

        # Sparql buttons' frame
        self.sparqlbuttons_frame = Frame(self.rdfsparql_frame)
        self.sparqlbuttons_frame.grid(row = 3, column = 4, padx = 20, pady = 3, columnspan = 4)

        # Sparql_Query button
        self.sparql_query_button = Button(self.sparqlbuttons_frame)
        self.sparql_query_button["text"] = "SPARQL Query"
        self.sparql_query_button["command"] =  self.sparql_query
        self.sparql_query_button.config( state = DISABLED )
        self.sparql_query_button.grid(row = 0, column = 0)

        # Sparql_Query button
        self.sparql_query_all_button = Button(self.sparqlbuttons_frame)
        self.sparql_query_all_button["text"] = "SPARQL Query *"
        self.sparql_query_all_button["command"] =  self.sparql_query_all
        self.sparql_query_all_button.config( state = DISABLED )
        self.sparql_query_all_button.grid(row = 0, column = 1)

        # Sparql_Subscription button
        self.sparql_subscription_button = Button(self.sparqlbuttons_frame)
        self.sparql_subscription_button["text"] = "SPARQL Subscription"
        self.sparql_subscription_button["command"] =  self.sparql_subscription
        self.sparql_subscription_button.config( state = DISABLED )
        self.sparql_subscription_button.grid(row = 0, column = 2)

        # SPARQL Active_Subs_Label Label
        self.sparql_active_subs_label = Label(self.rdfsparql_frame, text="SPARQL Active subs (0)")
        self.sparql_active_subs_label.grid(row = 4, column = 4, sticky = W, padx = 20, pady = 3)

        # SPARQL active subscriptions combobox
        self.sparql_active_subs_combobox_var = StringVar(self.rdfsparql_frame)
        self.sparql_active_subs_combobox_items = ()
        self.sparql_active_subs_combobox = OptionMenu(self.rdfsparql_frame, self.sparql_active_subs_combobox_var, self.sparql_active_subs_combobox_items)
        self.sparql_active_subs_combobox.config( state = DISABLED, width = 20 )
        self.sparql_active_subs_combobox.grid(row = 4, column = 5)

        # Sparql_Unsubscription button
        self.sparql_unsubscription_button = Button(self.rdfsparql_frame)
        self.sparql_unsubscription_button["text"] = "SPARQL Unsubscription"
        self.sparql_unsubscription_button["command"] =  self.sparql_unsubscription
        self.sparql_unsubscription_button.config( state = DISABLED )
        self.sparql_unsubscription_button.grid(row = 4, column = 6)

        # Notification frame
        self.notification_frame = LabelFrame(self.rdfsparql_frame)
        self.notification_frame.grid(row = 5, column = 0, columnspan = 8, sticky = E+W)
        self.notification_frame.config(relief = SUNKEN)

        # Notification Label
        self.notification_label = Label(self.notification_frame, text="Waiting for commands...")
        self.notification_label.pack(side = BOTTOM, padx = 10, pady = 10)

# main
if __name__ == "__main__":
    app = Application()
    app.show_frame(StartPage)
    app.mainloop()
