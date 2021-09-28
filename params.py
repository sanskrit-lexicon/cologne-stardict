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


regs = {'snp': [('<div n="P"/>', ''), ('<div n="lb"/>', ''), ],
'pgn': [('{%', ''), ('%}', ''), ],
'lan': [('{%', ''), ('%}', ''), ('{@', ''), ('@}', ''), ('<div n=', '\n<div n=')],
}

devaparams = {'snp': [('{%', '%}', 'iast')],
}
