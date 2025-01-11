from ast import literal_eval

def readConfig(configFile):
    parameters = {}

    with open(configFile, 'r', encoding='utf-8') as config:
        for lineNumber, line in enumerate(config):
            commentIndex = line.rfind('@')

            # Checking if @ symbol is in a string
            formattedLine = line[:commentIndex]
            if (formattedLine.count('\'')%2==1) or (formattedLine.count('\"')%2==1):
                commentIndex=-1

            if commentIndex!=-1:
                line=formattedLine

            line.lstrip(' ')
            line.rstrip(' ')
            line = line.replace(' =', '=')
            line = line.replace('= ', '=')

            if line in ('', ' ', '\n'):
                continue

            line = line.split('=')
            try:
                parameters[line[0]] = literal_eval(line[1])
            except Exception as error:
                print(f'CFGParser: line {lineNumber+1}, {error}, ignoring')

    return parameters

if __name__ == '__main__':
    print(readConfig('turtlecfg.txt'))
