
#allow printing in colors in the terminal if supported
try:
    import terminal

    def prettyText(text,design):
        if isinstance(design,str):
            return terminal.AnsiText(text,[design])
        elif isinstance(design,list):
            return terminal.AnsiText(text,design)
        else:
            return text

except ImportError, e:

    def prettyText(text,design):
        return text
