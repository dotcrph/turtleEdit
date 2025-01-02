from ast import literal_eval

def readConfig(configFile):
    parameters = {}

    with open(configFile, 'r') as config:
        for iteration, line in enumerate(config):
            commentIndex = line.find('@')

            if commentIndex!=-1:
                line=line[:commentIndex]

            line = line.replace(' ', '')

            line = line.split('=')
            try:
                parameters[line[0]] = literal_eval(line[1])
            except IndexError:
                pass
            except Exception as error:
                print(f'CFGParser: line {iteration+1}, {error}, ignoring')

    return parameters