
#==================================================
# Engine: engine-1 RUNNING
# Model: poker (python)
#
# Streams
#--------------------------------------------------
# stream-1     I:0  EOF    100,000 rps    99.7 mb/s
# -            I:4  EOF    100,000 rps    99.7 mb/s
# stream-2     O:1  
#
# Jets                           Input       Output
#--------------------------------------------------
# poker             EOF    100,000 rps  100,000 rps

ENGINE_LAYOUT = [
    ('fixed',  7, True),  # Engine:
    ('engine', 32, True),
]

MODEL_LAYOUT = [
    ('fixed', 7, True),  # Model:
    ('model', 32, True),
]

HEADER_LAYOUT = [
    ('col1', 20, True),
    ('col2', 16, False),
    ('col3', 12, False),
]

STREAM_LAYOUT = [
    ('name', 14, True),
    ('slot',  4, True),
    ('eof',   3, True),
    ('rps',  13, False),
    ('mbps', 12, False),
]

JET_LAYOUT = [
    ('name',   19, True),
    ('eof',     3, True),
    ('input',  13, False),
    ('output', 12, False),
]

def draw(layout, **kwargs):
    def fmt(text, width, left):
        align = '<' if left else '>'
        return '{:{align}{width}}'.format(text, width=width, align=align)
    return " ".join([ fmt(kwargs[name], width, left) for name,width,left in layout ])

def field(field, layout):
    pos = 0
    for name,width,_ in layout:
        if name == field:
            return (pos,width)
        pos += width + 1

