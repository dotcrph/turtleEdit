import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from datetime import datetime
from os import listdir
from os.path import isfile, isdir, join
import sys
import turtlecfgparser as cfgparser

# Widgets declaration
root = tk.Tk()
root.title('turtleEdit')

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
        'footerRelief': 'flat',
        'footerText': ['cursorPos', 'systemTime', 'openedFile', 'logMessage', 'appVersion'],
        'footerTextSeparator': ' | ',
        'footerTimeFormat': '%A %x %X'}
userConfig = defaultConfig.copy()

linesCount = 1
linesCountPrev = 1

logMessage = ''
appVersion = 'turtleEdit 1.1.0'

openedFile = None
currentFullscreen = None
currentTextSize = None

# Constructor functions
def setupConfig():
    # Read config file
    try:
        config = cfgparser.readConfig('turtlecfg.txt')
    except Exception as error:
        writeToLog(f'Invalid config! ({error})')
        return

    # Change current config
    for key, value in defaultConfig.items():
        if not key in config:
            if key in defaultConfig:
                userConfig[key] = defaultConfig[key]
            continue

        customValue = config[key]
        if isinstance(customValue, type(value)):
            userConfig[key] = config[key]

    # Clean footerText
    filteredFooterText = []
    for key in userConfig['footerText']:
        if key in ('cursorPos', 'systemTime') or key in globals():
            filteredFooterText.append(key)
            continue
        writeToLog(f'Invalid key {key} in \'footerText\'!')
    userConfig['footerText'] = filteredFooterText

def configureWidgets():
    global currentFullscreen, currentTextSize

    # Root
    root.geometry(userConfig['rootGeometry'])
    try:
        root.iconbitmap('turtleicon.ico')
    except Exception:
        writeToLog('Invalid app icon!')
    currentFullscreen = userConfig['rootFullscreen']
    root.attributes('-fullscreen', currentFullscreen)

    # Text
    text.configure(yscrollcommand=updateTextScroll)
    currentTextSize = userConfig['textFontSize']
    text.configure(bg=userConfig['textBg'],
                   fg=userConfig['textFg'],
                   font=(userConfig['textFont'], currentTextSize),
                   relief=userConfig['textRelief'],
                   wrap='none')
    text.configure(insertbackground=userConfig['insertColor'],
                   insertwidth=userConfig['insertWidth'])

    # Lines
    lines.configure(bg=userConfig['linesBg'],
                    fg=userConfig['linesFg'],
                    font=(userConfig['textFont'], currentTextSize),
                    relief=userConfig['linesRelief'],
                    wrap='none')

    # Footer
    if footer:
        footer.configure(anchor='w')
        footer.configure(bg=userConfig['footerBg'],
                        fg=userConfig['footerFg'],
                        font=(userConfig['footerFont'], userConfig['footerFontSize']),
                        relief=userConfig['footerRelief'])
        updateFooter()

def initializeWidgets():
    root.rowconfigure(0, weight=1)

    if userConfig['linesOnLeft']:
        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=1)
        text.grid(row=0, column=1, sticky='news')
        lines.grid(row=0, column=0, sticky='ns')
    else:
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=0)
        text.grid(row=0, column=0, sticky='news')
        lines.grid(row=0, column=1, sticky='ns')

    if userConfig['enableFooter']:
        footer.grid(row=1, column=0, columnspan=2, sticky='news')


# Utility functions
def reloadEditor(_):
    setupConfig()

    text.grid_forget()
    lines.grid_forget()
    footer.grid_forget()

    configureWidgets()
    initializeWidgets()
    writeToLog('Reloaded config')
    updateFooter()

def loadConfig(_):
    newConfigFile = askopenfilename(filetypes=[('Text Files', "*")])
    if not newConfigFile:
        return

    try:
        with open('turtlecfg.txt', 'w', encoding='utf-8') as oldConfig:
            with open(newConfigFile, 'r', encoding='utf-8') as newConfig:
                oldConfig.write(newConfig.read())
    except Exception as error:
        writeToLog(f'Failed to load config! ({error})')
        return

    reloadEditor(_)

def openFile(_):
    global openedFile, logMessage

    fileToOpen = askopenfilename(filetypes=[('Text Files', "*")])
    if not fileToOpen:
        return

    text.delete(1.0, tk.END)
    try:
        with open(fileToOpen, 'r', encoding='utf-8') as file:
            text.insert(tk.END, file.read())
    except Exception as error:
        writeToLog(f'Invalid file! ({error})')
        openedFile = None
        root.title('turtleEdit')
    else:
        openedFile = fileToOpen
        root.title(f'turtleEdit - {openedFile}')
        logMessage = ''
        updateFooter()

    updateLines()

def saveFile(_):
    if not openedFile:
        saveAsFile(_)
        return

    try:
        with open(openedFile, 'w', encoding='utf-8') as file:
            file.write(text.get(1.0, tk.END))
    except Exception as error:
        writeToLog(f'Failed saving file! ({error})')
    else:
        root.title(f'turtleEdit - {openedFile}')
        writeToLog('File saved successfully!')

def saveAsFile(_):
    global openedFile

    saveAsFilepath = asksaveasfilename(filetypes=[('Text Files', "*")])

    if not saveAsFilepath:
        return

    try:
        with open(saveAsFilepath, 'w', encoding='utf-8') as file:
            file.write(text.get(1.0, tk.END))
    except Exception as error:
        writeToLog(f'Failed saving file! ({error})')
    else:
        openedFile = saveAsFilepath
        root.title(f'turtleEdit - {openedFile}')
        writeToLog('File saved successfully!')

def clearFile(_):
    global openedFile

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
    currentFont = userConfig['textFont']

    text.configure(font=(currentFont, currentTextSize))
    lines.configure(font=(currentFont, currentTextSize))

def decreaseTextSize(_):
    global currentTextSize

    currentTextSize -= 1
    currentFont = userConfig['textFont']

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
    global linesCount, linesCountPrev
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
    if not footer:
        return

    cursorPos = text.index(tk.INSERT)
    systemTime = datetime.now().strftime(userConfig['footerTimeFormat'])

    values = []
    for key in userConfig['footerText']:
        try:
            value = eval(key)
        except Exception as error:
            print(f'Invalid key {key} in \'footerText\'! ({error})')

        if (value is None) or (value == ''):
            continue

        values.append(value)

    footerText = userConfig['footerTextSeparator'].join(values)
    footer.configure(text=footerText)

def updateFooterLoop():
    if not footer:
        return

    if 'systemTime' not in userConfig['footerText']:
        return

    updateFooter()
    sleepTime = (1000000 - datetime.now().microsecond)//1000
    footer.after(sleepTime, updateFooterLoop)

def updateTextScroll(_, pos):
    offset = text.yview()[0]
    lines.yview_moveto(offset)

def onKeyPress(_):
    updateFooter()

def onKeyRelease(_):
    updateFooter()
    updateLines()

# Binds config setup
try:
    binds = cfgparser.readConfig('turtlebinds.txt')
except Exception as error:
    writeToLog(f'Invalid binds! ({error})')
    binds = {}

# Binds setup
def createBindings():
    text.bind('<ButtonRelease-1>', onKeyPress)
    #text.bind('<Button-1>', onKeyPress)
    text.bind('<B1-Motion>', onKeyPress)
    text.bind('<KeyPress>', onKeyPress)
    text.bind('<KeyRelease>', onKeyRelease)

    # Parameters
    for key, value in binds.items():
        try:
            root.bind(key, eval(value))
        except Exception as error:
            writeToLog(f'Invalid bind! ({error}), ignoring')

initFunctions = [setupConfig, configureWidgets]
mainFunctions = [initializeWidgets, createBindings]

if __name__ == '__main__':
    # Load plugins
    if not isdir('Plugins'):
        writeToLog('\'Plugins\\\' directory is not found!')
    else:
        for plugin in listdir('Plugins'):
            pluginDirectory = join('Plugins', plugin)

            if not isfile(pluginDirectory):
                continue

            try:
                with open(pluginDirectory, 'r', encoding='utf-8') as pluginFile:
                    compiledPlugin = compile(pluginFile.read(), plugin, 'exec')
                exec(compiledPlugin)
            except Exception as error:
                writeToLog(f'Invalid plugin {plugin}! ({error})')
            else:
                print(f'Successfully loaded {plugin}')

    # Call init functions
    for function in initFunctions:
        function()

    # Remove extra line at line 0
    updateLines()
    lines.configure(state='normal')
    lines.delete('1.0')
    lines.configure(state='disabled')

    # Call main functions
    for function in mainFunctions:
        function()

    updateFooterLoop()
    root.mainloop()
