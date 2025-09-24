import fitz
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

import sys
import speech_recognition as sr
import difflib
import copy

microphoneIndex=0
initialCommands=["turn left", "go left", "previous", "previous page", "go back", "back", "turn right", "go right", "next", "next page", "go forward", "forward", "stop", "quit"]
leftCommands=["turn left", "go left", "previous", "previous page", "go back", "back"]
rightCommands=["turn right", "go right", "next", "next page", "go forward", "forward"]
selectCommands=[]
#selectCommands=["Go to page ", "Go to"]
stopCommands=["stop", "quit"]
commands=copy.deepcopy(initialCommands)
pdf=None
#width=1500
#height=1000
#from screeninfor import get_monitors
#monitor=get_monitors()[0]

class fileHandler():
    def countPages(self):
        self.pages=0
        self.zoomFactor=1
        for page in self.doc:
            self.pages+=1
        return self.pages
    def setZoomFactor(self, zoomFactor):
        self.zoomFactor=zoomFactor
    def calculateZoomFactor(self, width, height):
        image=self.getUnzoomedImage()
        imageWidth=image.width
        imageHeight=image.height
        zoomX=width/(imageWidth)
        zoomY=height/(imageHeight)
        self.zoomFactor=min(zoomX, zoomY)
        print("New zoom factor - ",self.zoomFactor)
    def __init__(self, filename):
        self.filename=filename
        self.doc=fitz.open(self.filename)
        self.countPages()
        self.currentPage=0
        self.createSelectCommands()
    def getFilename(self):
        return self.filename
    def getCurrentPage(self):
        return self.currentPage
    def setPage(self, newPage):
        self.currentPage=newPage
        if self.currentPage>self.pages:
            self.currentPage=self.pages
        if self.currentPage<0:
            self.currentPage=0
    def movePage(self, offset):
        self.setPage(self.currentPage+offset)
    def loadPage(self, pageNumber):
        if pageNumber>=0 and pageNumber<self.pages:
            return self.doc.load_page(pageNumber)
        else:
            return self.doc.load_page(self.pages-1)
    def getUnzoomedImage(self):
        page=self.loadPage(self.currentPage)
        matrix=fitz.Matrix(1,1)
        pixels = page.get_pixmap(matrix=matrix)
        return Image.frombytes("RGB", [pixels.width, pixels.height], pixels.samples)
    def getImageFromPage(self, pageNumber):
        page=self.loadPage(pageNumber)
        matrix = fitz.Matrix(self.zoomFactor, self.zoomFactor)
        pixels = page.get_pixmap(matrix=matrix)
        return Image.frombytes("RGB", [pixels.width, pixels.height], pixels.samples)
    def getPageImage(self):
        return self.getImageFromPage(self.currentPage)
    def getPageImageOffset(self, offset):
        return self.getImageFromPage(self.currentPage+offset)
    def getZoomedPageImage(self, pageNumber, zoomFactor):
        print("getZoomedPageImage -", pageNumber)
        page=self.getPageImage(pageNumber)
        matrix=fitz.Matrix(zoomFactor,zoomFactor)
        pixels=page.get_pixmap(matrix=matrix)
        return Image.frombytes("RGB", [pixels.width, pixels.height], pixels.samples)
    def createSelectCommands(self):
        global selectCommands, commands
        commands=copy.deepcopy(initialCommands)
        selectCommands=[]
        for i in range(self.pages):
            selectCommands.append("go to page "+str(i))
            commands.append("go to page "+str(i))
            selectCommands.append(str(i))
            commands.append(str(i))
        print("Select commands - ")
        print(selectCommands)
        print("Commands - ")
        print(commands)

class pdfDisplayer():
    def __init__(self, files):
        global width, height
        if len(files)>0:
            self.files=files
            self.currentFile=len(self.files)-1
        else:
            self.files=[fileHandler("Giuliani - Scelta di studi per chitarra - Chiesa.pdf")]
            self.currentFile=0
        self.root = Tk()
        
        self.numberOfPages=1
        height=self.root.winfo_screenheight()-120
        width=int(height*0.707)*self.numberOfPages
        self.menubar=Menu(self.root)
        self.root.config(menu=self.menubar)
        self.fileMenu=Menu(self.menubar)
        self.updateFileMenu()
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        self.width=width
        self.height=height
        self.root.geometry(str(self.width)+"x"+str(self.height))
        self.canvas=Canvas(self.root)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)
        #self.scrollbar = Scrollbar(self.root)
        #self.scrollbar.pack(side=RIGHT, fill=Y)
        self.displayer=self.files[self.currentFile]
        self.root.title(self.displayer.getFilename())
        self.frame=Frame(self.canvas)
        self.frame.pack(side=TOP, fill=BOTH, expand=1)
        self.footer=Frame(self.canvas)
        self.entry=Entry(self.frame)
        self.entry.insert(0, '1')
    def changeFile(self):
        filename=filedialog.askopenfilename(initialdir="/", title="Select a music sheet.", filetypes = (("Text files", "*.txt"), ("PDF files", "*.pdf"), ("All files", "*.")))
        #self.fileLabel.configure(text="Opened file"+filename)
        index = self.getFilenameIndex(filename)
        if index==None:
            print("NEW FILE!")
            self.files.append(fileHandler(filename))
            print(self.files)
            self.currentFile=len(self.files)-1
        else:
            self.currentFile=index
            print("File already at",index)
        self.displayer=self.files[self.currentFile]
        self.updateDisplay()
        self.root.title(filename)
        self.updateFileMenu()
    def getFileIndex(self, file):
        for i in range(len(self.files)):
            if self.files[i]==file:
                return i
        return None
    def getFilenameIndex(self, filename):
        for i in range(len(self.files)):
            if self.files[i].getFilename()==filename:
                return i
        return None
    def addFile(self, newFile):
        self.files.append(newFile)
    def updateFileMenu(self):
        self.fileMenu=Menu(self.menubar)
        for i in range(len(self.files)):
            file=self.files[i]
            def tempLoadCommand():
                print("Loading",file.getFilename())
                index=self.getFileIndex(file)
                self.files.pop(index)
                self.files.append(file)
                self.updateFileMenu()
                self.currentFile=index
                self.displayer=self.files[index]
                self.updateDisplay()
            self.fileMenu.add_command(label=file.getFilename(),command=tempLoadCommand)
            print(self.files[i].getFilename())
        self.fileMenu.add_command(label="Exit",command=self.quit)
        self.fileMenu.add_command(label="Load new file",command=self.changeFile)
    def setPage(self, pageNumber):
        self.displayer.setPage(pageNumber)
        self.updateDisplay()
    def movePage(self, offset):
        self.displayer.movePage(offset)
        self.updateDisplay()
    def prevPage(self):
        self.movePage(-self.numberOfPages)
    def nextPage(self):
        self.movePage(self.numberOfPages)
    def goToPageFromEntry(self):
        self.displayer.setPage(int(self.entry.get()) - 1)
        self.updateDisplay()
    def updateDisplayDimensions(self, windowWidth, windowHeight):
        self.displayer.calculateZoomFactor(windowWidth*2/self.numberOfPages, windowHeight)
        #self.displayer.setZoomFactor(1)
        label=Label(self.root, text="Enter page number to display")
        image1=self.displayer.getPageImage()
        image2=self.displayer.getPageImageOffset(1)
        tk1=ImageTk.PhotoImage(image1)
        tk2=ImageTk.PhotoImage(image2)

        panel1 = Label(self.frame, image=tk1)
        panel1.grid(row=0, column=0, columnspan=3)
        self.frame.image1 = tk1
        if self.numberOfPages>1:
            panel2 = Label(self.frame, image=tk2)
            panel2.grid(row=0, column=3, columnspan=3)
            self.frame.image2 = tk2
        
        leftButton=Button(self.footer, text="Previous page", command=self.prevPage)
        selectButton=Button(self.footer, text="Go to selected page",
                            command=self.goToPageFromEntry)
        rightButton=Button(self.footer, text="Next page", command=self.nextPage)
        for i in range(3):
            self.footer.grid_columnconfigure(i, weight=1, uniform="footer")
        leftButton.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        selectButton.grid(row=1, column=1, sticky="ew", padx=4, pady=4)
        rightButton.grid(row=1, column=2, sticky="ew", padx=4, pady=4)
        self.entry.grid(row=2, column=1, sticky="ew", padx=4, pady=4)
        self.footer.pack(side=BOTTOM, fill=X)
        self.canvas.create_window(0, 0, anchor="nw", window=self.frame)
        self.frame.update_idletasks()
        #self.canvas.config(scrollregion=self.canvas.bbox("all"))
        #self.canvas.config(yscrollcommand=self.scrollbar.set)
        print("Displayed")
    def updateDisplay(self):
        x,y,pageFrameWidth,pageFrameHeight=self.root.grid_bbox(0, 0)
        windowWidth, windowHeight=self.root.winfo_width(), self.root.winfo_height()-60
        print(windowWidth, windowHeight)
        self.updateDisplayDimensions(windowWidth, windowHeight)
    def setDisplayer(self, newDisplayer):
        self.displayer=newDisplayer
        self.updateDisplay()
    def mainloop(self):
        self.root.mainloop()
    def quit(self):
        self.root.destroy()
    def createSelectCommands(self):
        self.displayer.createSelectCommands()

import threading
class Microphone(threading.Thread):
    def __init__(self):
        super(Microphone, self).__init__()
    def listenForCommand(self, microphoneIndex, commands):
        recogniser = sr.Recognizer()
        with sr.Microphone(device_index=microphoneIndex) as source:
            print("Listening for audio.")
            recogniser.adjust_for_ambient_noise(source)
            try:
                audio = recogniser.listen(source)
                textFromAudio = recogniser.recognize_google(audio).lower()
                print(textFromAudio)
                return textFromAudio
                #matchFromText = difflib.get_close_matches(textFromAudio, commands, n=1, cutoff=0.7)
                #if matchFromText:
                #    print(matchFromText)
                #    return matchFromText[0]
                #else:
                #    print("No match found.")
            except sr.UnknownValueError:
                print("Couldn't understand audio.")
            except sr.RequestError:
                print("Library couldn't receive results, check your internet.")
        return None
    def run(self):
        global microphoneIndex, commands, pdf
        global commands, initialCommands, leftCommands, rightCommands, stopCommands, selectCommands
        #leftCommands=["turn left", "go left", "previous", "previous page"]
        #rightCommands=["turn right", "go right", "next", "next page"]
        #selectCommands=["Go to page ", "Go to"]
        #stopCommands=["stop","quit"]
        pdf.createSelectCommands()
        loop=True
        while loop:
            command = self.listenForCommand(microphoneIndex, commands)
            print("Command -", command)
            #if command!=None:
            #    words = command.split(' ')
            #    if words[len(words)-1].isdigit():
            #        lastWord=int(words.pop(len(words)-1))
            #        print("split result - ",  words, lastWord)
            #        if words.join(' ') in selectCommands:
            #            print("Going to page",lastWord)
            #            pdfDisplayer.goToPage(lastWord)
            if command in selectCommands:
                print("Select command detected.")
                words = command.split(' ')
                if words[len(words)-1].isdigit():
                    lastWord=int(words.pop(len(words)-1))
                    print("split result - ",  words, lastWord)
                    print("Going to page",lastWord)
                    pdf.setPage(lastWord)
                else:
                    print("Desired page is not a number.")
            elif command in leftCommands:
                pdf.prevPage()
            elif command in rightCommands:
                pdf.nextPage()
            elif command in stopCommands:
                loop=False
                pdf.quit()
                exit()
            else:
                print(command,"is not a valid command")

demo=fileHandler("Giuliani - Scelta di studi per chitarra - Chiesa.pdf")
demo2=fileHandler("Asturias - Thoralksson.pdf")
pdf=pdfDisplayer([demo, demo2])
pdf.updateDisplayDimensions(width, height-60)
pdf.updateDisplay()

microphoneIndex=0
mic=Microphone()
mic.start()

pdf.mainloop()
