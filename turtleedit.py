import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import turtlecfgparser as cfgparser
import time
import sys


# Widgets declaration
root = tk.Tk()
text = tk.Text(root)
lines = tk.Text(root)
footer = tk.Label(root)

# Variables declaration
defaultConfig = {'rootGeometry': '1600x900', 
        'rootFullscreen': False, 
        'textBg': 'black', 
        'textFg': 'white', 
        'textFont': 'Consolas', 
        'textFontSize': 16, 
        'textRelief': 'flat',
        'insertColor': 'white',
        'insertWidth': 3,
        'linesOnLeft': True,
        'linesBg': 'white', 
        'linesFg': 'black',
        'linesRelief': 'flat',
        'enableFooter': True, 
        'footerBg': 'white', 
        'footerFg': 'black', 
        'footerFont': 'Consolas', 
        'footerFontSize': 16, 
        'footerRelief': 'flat'}
config = None

linesCount = 1
linesCountPrev = 1

logMessage = ''
appVersion = 'turtleEdit 1.0'

openedFile = None
currentFullscreen = None 
currentTextSize = None

# Constructor functions
def setupConfig():
    global config, defaultConfig, logMessage
    try:
        config = cfgparser.readConfig('turtlecfg.txt')
    except Exception as error:
        writeToLog(f'Invalid config! ({error})')
        config = defaultConfig

def readConfigValue(key, expectedType):
    global defaultConfig, config, logMessage
    
    if key not in config.keys():
        return defaultConfig[key]

    value = config[key]
    if type(value) is not expectedType:
        writeToLog(f'Wrong value type in config! (key: {key}, type: {type(value)}, expected: {expectedType})')
        return defaultConfig[key]

    return value

def configureWidgets():
    global root, text, lines, footer, currentFullscreen, currentTextSize

    # Root
    root.title('turtleEdit')
    root.geometry(readConfigValue('rootGeometry', str))
    try:
        root.iconbitmap('turtleicon.ico')
    except: 
        writeToLog('Invalid app icon!')
    currentFullscreen = readConfigValue('rootFullscreen', bool)
    root.attributes('-fullscreen', currentFullscreen)

    # Text
    text.configure(yscrollcommand=updateTextScroll)
    currentTextSize = readConfigValue('textFontSize', int)
    text.configure(bg=readConfigValue('textBg', str), fg=readConfigValue('textFg', str), 
                   font=(readConfigValue('textFont', str), currentTextSize), wrap='none', relief=readConfigValue('textRelief', str))
    text.configure(insertbackground=readConfigValue('insertColor', str), insertwidth=readConfigValue('insertWidth', int))
    
    # Lines
    updateLines(); lines.configure(state='normal'); lines.delete('1.0'); lines.configure(state='disabled')
    lines.configure(yscrollcommand=updateTextScroll)
    lines.configure(bg=readConfigValue('linesBg', str), fg=readConfigValue('linesFg', str), 
                    font=(readConfigValue('textFont', str), currentTextSize), wrap='none', relief=readConfigValue('linesRelief', str))

    # Footer
    if footer:
        footer.configure(anchor='w')
        footer.configure(bg=readConfigValue('footerBg', str), fg=readConfigValue('footerFg', str),
                        font=(readConfigValue('footerFont', str), readConfigValue('footerFontSize', int)), 
                        relief=readConfigValue('footerRelief', str))

def initializeWidgets():
    global root, text, lines, footer

    root.rowconfigure(0, weight=1)

    if readConfigValue('linesOnLeft', bool):
        root.columnconfigure(1, weight=1)
        text.grid(row=0, column=1, sticky='news')
        lines.grid(row=0, column=0, sticky='ns')
    else:
        root.columnconfigure(0, weight=1)
        text.grid(row=0, column=0, sticky='news')
        lines.grid(row=0, column=1, sticky='ns')

    if readConfigValue('enableFooter', bool):
        footer.grid(row=1, column=0, columnspan=2, sticky='news')


# Utility functions
def openFile(_):
    global root, text, openedFile, logMessage

    openedFile = askopenfilename(filetypes=[('Text Files', "*")])
    if not openedFile: return

    text.delete(1.0, tk.END)
    try:
        with open(openedFile, 'r') as file:
            text.insert(tk.END, file.read())
    except Exception as error:
        writeToLog(f'Invalid file! ({error})')
        openedFile = None
        root.title('turtleEdit')
    else:
        text.delete('end-2c', 'end') # Deletes extra line
        root.title(f'turtleEdit - {openedFile}')
        logMessage = ''
        updateFooter()
    
    updateLines()

def saveFile(_):
    global root, text, openedFile, logMessage

    if not openedFile: 
        saveAsFile(_)
        return
    
    try:
        with open(openedFile, 'w') as file:
            file.write(text.get(1.0, tk.END))
    except Exception as error:
        writeToLog(f'Failed saving file! ({error})')
    else:
        root.title(f'turtleEdit - {openedFile}')
        writeToLog('File saved successfully!')

def saveAsFile(_):
    global root, text, openedFile, logMessage

    saveAsFilepath = asksaveasfilename(filetypes=[('Text Files', "*")])
    if not saveAsFilepath: return

    try:
        with open(saveAsFilepath, 'w') as file:
            file.write(text.get(1.0, tk.END))
    except Exception as error:
        writeToLog(f'Failed saving file! ({error})')
    else:
        openedFile = saveAsFilepath
        root.title(f'turtleEdit - {openedFile}')
        writeToLog('File saved successfully!')

def clearFile(_):
    global root, text, openedFile, logMessage

    saveAsFile(_)
    text.delete(1.0, tk.END)
    openedFile = None
    root.title('turtleEdit')

    updateLines()
    updateFooter()

def quitWithSave(_):
    saveFile(_)
    sys.exit(0)

def quitWithoutSave(_):
    sys.exit(0)

def writeToLog(string):
    global logMessage
    logMessage = string
    print(logMessage)
    updateFooter()

def clearLogMessage(_):
    global logMessage
    logMessage = ''
    updateFooter()

def increaseTextSize(_):
    global currentTextSize

    currentTextSize += 1
    currentFont = readConfigValue('textFont', str)

    text.configure(font=(currentFont, currentTextSize))
    lines.configure(font=(currentFont, currentTextSize))

def decreaseTextSize(_):
    global currentTextSize

    currentTextSize -= 1
    currentFont = readConfigValue('textFont', str)

    text.configure(font=(currentFont, currentTextSize))
    lines.configure(font=(currentFont, currentTextSize))

def changeFullscreen(_):
    global currentFullscreen
    currentFullscreen = not currentFullscreen
    root.attributes('-fullscreen', currentFullscreen)

def setText(t, val):
    t.delete(1.0, tk.END)
    t.insert(tk.END, val)

def updateLines():
    global linesCount, linesCountPrev, lines
    linesCount = text.index('end-1c')
    linesCount = int(linesCount[:linesCount.find('.')])+1
    linesDiff = linesCount-linesCountPrev

    lines.configure(state='normal')
    if linesDiff>0:
        for i in range(linesDiff):
            lines.insert(tk.END, '\n'+str(linesCountPrev+i))
    elif linesDiff<0:
        lines.delete(f'{linesCount}.0', tk.END)
    lines.configure(state='disabled')

    linesCountPrev = linesCount
    lines.configure(width=len(str(linesCount-1)))
    updateTextScroll(None,None)

def updateFooter():
    global text, logMessage, footer

    if not footer: 
        return

    cursorPos = text.index(tk.INSERT)
    systemTime = time.strftime('%I:%M:%S')

    footerText = f'{cursorPos} | {systemTime}'
    if openedFile: footerText += f' | {openedFile}'
    if logMessage: footerText += f' | {logMessage}'
    footerText += f' | {appVersion}'

    footer.configure(text=footerText)

def updateFooterLoop():
    global footer

    if not footer:
        return

    updateFooter()
    footer.after(1000, updateFooterLoop) # For updating system clock

def updateTextScroll(_, pos):
    global text, lines
    offset = text.yview()[0]
    lines.yview_moveto(offset)

def onKeyPress(_):
    updateFooter()

def onKeyRelease(_):
    updateFooter()
    updateLines()

# Binds setup
try:
    binds = cfgparser.readConfig('turtlebinds.txt')
except Exception as error:
    writeToLog(f'Invalid binds! ({error})')
    binds = {}


def createBindings():
    global root, logMessage

    text.bind('<B1-Motion>', onKeyPress)
    text.bind('<KeyPress>', onKeyPress)
    text.bind('<KeyRelease>', onKeyRelease)

    # Parameters
    for key, value in binds.items():
        try:
            root.bind(key, eval(value))
        except Exception as error:
            writeToLog(f'Invalid bind! ({error}), ignoring')


if __name__ == '__main__':
    setupConfig()
    configureWidgets()
    initializeWidgets()
    createBindings()
    updateFooterLoop()
    
    root.mainloop()