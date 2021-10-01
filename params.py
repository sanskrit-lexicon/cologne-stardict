meaningseparator = {'acc': ('([ .])--', r'\g<1>BREAK --'),
'md': (';', ';BREAK'),
'ap90': ('<b>', 'BREAK<b>'),
'ben': (' <b>', 'BREAK <b>'),
'bhs': ('([(]<b>[0-9]+</b>[)])', r'BREAK\g<1>'),
'bop': (r' ([0-9]+\))', r'BREAK\g<1>'),
'bor': ('<div n="I">', 'BREAK'),
'cae': (';', ';BREAK'),
'ccs': (';', ';BREAK'),
'gra': ('(<div n="[PH])', r'BREAK\g<1>'),
'gst': ('(<div n="P)', r'BREAK\g<1>'),
'ieg': ('; ', ';BREAK'),
'mci': ('<b>', 'BREAK<b>'),
'mw72': (r'\—', r'BREAK—'),
'mwe': ('.--', 'BREAK--'),
'ap': ('<lb></lb>[.]', '<lb></lb>BREAK'),
'pui': ('</F>', '</F>BREAK'),
'shs': ('([).]) ([0-9nmf]+[.])', r'\g<1>BREAK \g<2>'),
'snp': ('<P></P>', 'BREAK<P></P>'),
'stc': (';', ';BREAK'),
'wil': (' ([mfn]+)[.]', r'BREAK\g<1>.'),
'yat': ('<i>', 'BREAK<i>'),
'ae': ('<b>-', 'BREAK<b>-')}


regs = {
'ae': [('{@([0-9]+)', ' \n\t\t\g<1>'), ('@}', ''), ('{@-', '\n-'), ('{@', ''), ('{%-', '\n\t{%'), ('%}', ''), ('{%', ''), ],
'ap90': [('{@([0-9]+)', ' \n\g<1>'), ('@}', ''), ('{@-', '\n-'), ('{@', ''), ('{%', ''), ('%}', ''), (' {#--', ' \n--{#'), ],
'acc': [('\.--', '\n.--'), ('<HI>', '\n\t\t<HI>'), ('<HI1>', '\n\t\t<HI1>'), ],
'lan': [('{%', ''), ('%}', ''), ('{@', ''), ('@}', ''), ],
'ben': [('{@', '\n '), ('@}', ''), ('{%([^<]*[-][,])%}', '\n{%\g<1>%}')],
'bhs': [('\({@([0-9]+)@}\)', '\n(\g<1>)'), ('{@', ''), ('@}', ''), ('{%', ''), ('%}', ''), ],
'bop': [('([0-9]+\))', '\n\g<1>'), ('{%', ''), ('%}', ''), ],
'bor': [('<div n="', '\n<div n="'), ('{@', ''), ('@}', ''), ('{%', ''), ('%}', ''), ],
'bur': [('\|\|', '\n\t\t'), ('-- {%', '\n\t-- {%')],
'cae': [(';', ';\n'), ],
'ccs': [(';', ';\n'), ('{%', ''), ('%}', ''), ('{#°', '\n{#°'), ],
'gra': [('(<div n="[PH])', r'\n\g<1>'),  ('{@', ''), ('@}', ''), ('{%', ''), ('%}', ''), ],
'gst': [('<div n="P', '\n<div n="P'), ('<sup>', '\n\t<sup>'), ('{%', ''), ('%}', ''), ],
'ieg': [('{%', ''), ('%}', ''), ],
'inm': [('{%', ''), ('%}', ''), ('{@', ''), ('@}', ''), ],
'krm': [('{@', ''), ('@}', ''), ],
'lan': [('{%', ''), ('%}', ''), ('{@', ''), ('@}', ''), ],
'pgn': [('{%', ''), ('%}', ''), ],
'snp': [('<div n="P"/>', ''), ('<div n="lb"/>', ''), ],
}

devaparams = {'snp': [('{%', '%}', 'iast')],
'ben': [('{%', '%}', 'iast'), ('{#', '#}', 'slp1')],
'bur': [('{%', '%}', 'iast'), ('{#', '#}', 'slp1')],
'krm': [('<s>', '</s>', 'slp1')],
}
