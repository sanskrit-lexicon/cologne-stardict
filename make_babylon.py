# This Python file uses the following encoding: utf-8
"""
Usage:
python make_babylon.py pathToDicts dictId [0/1]
0 for viewing (\n line break), 1 for production (More HTML like line break)
e.g.
python make_babylon.py input/extracted/pywork md 1
"""
import re,codecs,sys
from lxml import etree
import transcoder
import datetime

# Function to return timestamp
def timestamp():
	return datetime.datetime.now()

# Function to read normalized headwords (hwnorm1c.txt) into a dict
# Returns a dict with headword as key and the list of associated headwords as value.
def readhwnorm1c():
	fin = codecs.open('input/hwnorm1c.txt','r','utf-8')
	lines = fin.readlines()
	output = {}
	for line in lines:
		line = line.strip()
		chunks = line.split(';')
		words = []
		if len(chunks) > 1:
			baseword = chunks[0].split(':')[0]
			for chunk in chunks[1:]:
				worddictsep = chunk.split(':')
				word = worddictsep[0]
				dicts = worddictsep[-1].split(',')
				if not baseword == word:
					result = [baseword,word]
					output[word] = (result,dicts)
	return output

def licencetext(dictId):
	fin = codecs.open('../Cologne_localcopy/'+dictId+'/'+dictId+'txt/'+dictId+'header.xml','r','utf-8')
	data = fin.read()
	fin.close()
	return data
	
if __name__=="__main__":
	pathToDicts = sys.argv[1]
	dictId = sys.argv[2]
	production = sys.argv[3]
	#dictList = ['acc','ae','ap','ap90','ben','bhs','bop','bor','bur','cae','ccs','gra','gst','ieg','inm','krm','mci','md','mw','mw72','mwe','pd','pe','pgn','pui','pw','pwg','sch','shs','skd','snp','stc','vcp','vei','wil','yat']
	
	#licence = licencetext(dictId).strip()
	#licence = licence.replace('\n','<BR>')
	
	# Read a list of normalized headwords. See https://github.com/sanskrit-coders/stardict-sanskrit/issues/66.
	hwnormlist = readhwnorm1c()
	lnumEntryDict = {}
	meaningseparator = {'acc':('([ .])--','\g<1>BREAK --'), 
	'md':(';',';BREAK'), 
	'ap90':('<b>[-]{2}([0-9]+)</b>','BREAK<b>\g<1></b>'), 
	'ben':(' <b>','BREAK <b>'), 
	'bhs':('([(]<b>[0-9]+</b>[)])','BREAK\g<1>'), 
	'bop':(' ([0-9]+\))', 'BREAK\g<1>'), 
	'bor':('<div n=\"[I1]\">','BREAK'), 
	'cae':(';',';BREAK'), 
	'ccs':(';',';BREAK'), 
	'gra':('<P1></P1>','BREAK'), 'gst':('<P></P>','BREAK'), 'ieg':('; ',';BREAK'), 'mci':('<b>','BREAK<b>'), 'mw72':('<i>--','BREAK<i>--'), 'mwe':('.--','BREAK--'), 'ap':('<lb></lb>[.]','<lb></lb>BREAK'), 'pui':('</F>','</F>BREAK'), 'shs':('([).]) ([0-9nmf]+[.])','\g<1>BREAK \g<2>'), 'snp':('<P></P>','BREAK<P></P>'), 'stc':(';',';BREAK'), 'wil':(' ([mfn]+)[.]','BREAK\g<1>.'), 'yat':('<i>','BREAK<i>'), 'ae':('<b>-','BREAK<b>-')}
	if dictId in meaningseparator:
		instr = meaningseparator[dictId][0]
		outstr = meaningseparator[dictId][1]
	inputfile = pathToDicts+'/'+dictId+'.xml'
	tree = etree.parse(inputfile)
	hw = tree.xpath("/"+dictId+"/H1/h/key1")
	key2s = tree.xpath("/"+dictId+"/H1/h/key2")
	lnum = tree.xpath("/"+dictId+"/H1/tail/L")
	entry =  tree.xpath("/"+dictId+"/H1/body")
	
	if production == '0':
		outputfile = codecs.open('output/'+dictId+'.babylon','w','utf-8')
	elif production == '1':
		outputfile = codecs.open('production/'+dictId+'.babylon','w','utf-8')
		
	# Write licence text
	#outputfile.write('LICENCE.xml\n')
	#outputfile.write(unicode(licence)+u'\n\n')

	counter = 0
	for x in range(len(hw)):
		heading1 = etree.tostring(hw[x], method='text', encoding='utf-8')
		key2 = etree.tostring(key2s[x], method='text', encoding='utf-8')
		key2 = key2.decode('utf-8')
		ln = etree.tostring(lnum[x], method='text', encoding='utf-8')
		lnumEntryDict[ln] = etree.tostring(entry[x], method='html', encoding='utf-8')
		
		if counter % 1000 == 0:
			print counter
		counter += 1
		if heading1 in hwnormlist and dictId.upper() in hwnormlist[heading1][1]:
			possibleheadings = hwnormlist[heading1][0]
			print possibleheadings 
		else:
			possibleheadings = [heading1]
		"""
		if len(possibleheadings) > 1:
			print possibleheadings
		"""
		if dictId not in ['ae','mwe','bor']:
			heading = '|'.join([transcoder.transcoder_processString(head,'slp1','deva') for head in possibleheadings])
		else:
			heading = heading1
			
		html = lnumEntryDict[ln]
		# OLD ONE STARTS
		#text = etree.tostring(entry[x], method='text', encoding='utf-8')
		#html = etree.tostring(entry[x], method='html', encoding='utf-8')
		# OLD ONE ENDS
		html = re.sub('\[Page[0-9+ abc.-]+\]','',html)
		if dictId in ['ben']:
			html = html.replace('-</i> <lb></lb><i>', '')
		if dictId in ['mwe','skd','vcp']:
			html = html.replace('<lb></lb>',' ')
		elif dictId in ['ap']:
			html = re.sub('<lb></lb>[.]<b>','BREAK<b>',html)
			html = html.replace('<lb></lb>',' ')
		else:
			html = html.replace('<lb></lb>','')
		# If there are built in divs signifying breaks, add breaks there.
		html = html.replace('<div n="P">', 'BREAK<div n="P">')
		html = re.sub(' <gram','BREAK<gram',html)
		html = re.sub('([^(])<divm','BREAK\g<1><divm',html)
		html = re.sub('<div n="1"', 'BREAK<div n="1"', html)
		html = re.sub('<div n="2"', 'BREAK\t<div n="2"', html)
		html = re.sub('<div n="3"', 'BREAK\t\t<div n="3"', html)
		html = re.sub('<div n="4"', 'BREAK\t\t\t<div n="4"', html)
		if dictId in ['pd']:
			html = html.replace('<br>','')
		if dictId in ['sch']:
			html = re.sub('\[Schµ[0-9]+\]','',html)
			html = re.sub('€[0-9]+','',html)
			html = html.replace(' -- ','BREAK -- ')
		html = html.replace('<b>--Comp.</b>','BREAK<b>--Comp.</b>BREAK') # ap90
		if dictId in ['wil']:
			html = html.replace('¦ ','BREAK')
			html = html.replace('<body>.<s>','<body><s>')
			html = html.replace('.E.','BREAK.E.')
			html = html.replace('<br>','BREAK')
		html = html.decode('utf-8')
		if dictId in ['wil']:
			html = html.replace(u'²',u'\t')
		if dictId in ['ap']:
			html = html.replace(u'(-<i>',u'-(<i>')
			html = html.replace(u'<i>','BREAK<i>')
			html = html.replace('<b>','BREAK<b>')
		html = html.replace(u'<b><s>º',u'BREAK<b><s>º') # ap90
		if dictId in ['pd']:
			html = html.replace('<b>','BREAK<b>')
		#print html.encode('utf-8')
		
		if dictId in meaningseparator and re.search(instr,html):
			html = re.sub(instr,outstr,html)
		html = re.sub(u'[(](<b><s>--[a-zA-Z]+</s>)',u'BREAK\g<1>',html) # ap90
		if dictId in ['ben']:
			html = html.replace(u'¤10',u'') # BEN usually has dIrga mentioned and hrasva being mentioned by breve.
		if dictId in ['cae', 'ccs']:
			html = html.replace(u'BREAK</s>',u'</s>BREAK') # https://github.com/sanskrit-lexicon/cologne-stardict/issues/3#issuecomment-455857610
		if dictId in ['pwg']:
			html = html.replace('^', '/')
		sanskrittext = re.findall('<s>([^<]*)</s>',html)
		html = re.sub(u'(<s>--[a-zA-Z]+</s>)',u'BREAK\g<1>',html) # ap90
		for sans in sanskrittext:
			html = html.replace('<s>'+sans+'</s>','<s>'+transcoder.transcoder_processString(sans,'slp1','deva')+'</s>')
		if dictId in ['ben']:
			html = re.sub('<i>([^<]*[-][,])</i>','BREAK<i>\g<1></i>',html)
			html = html.replace('i. e.BREAK <i>','i.e. <i>')
		if dictId in ['ae']:
			html = re.sub('<i>-(.*)</i>','BREAK\t<i>\g<1></i>',html)
			html = re.sub('<b>([0-9]+)</b>','BREAK\t\t<b>\g<1></b>',html)
		if dictId in ['ben', 'bur', 'snp', 'stc', 'inm']:
			italictext = re.findall('<i>([^<]*)</i>',html)
			for ital in italictext:
				rep = ital.lower()
				rep = rep.replace('ch','c')
				rep = rep.replace('sh','z')
				rep = transcoder.transcoder_processString(rep,'roman','slp1')
				rep = transcoder.transcoder_processString(rep,'slp1','deva')
				html = html.replace('<i>'+ital+'</i>','<i>'+rep+'</i>')
		if dictId in ['stc','vei']:
			italictext = re.findall('<body><b>([^<]*)</b>',html)
			for ital in italictext:
				rep = ital.lower()
				rep = transcoder.transcoder_processString(rep,'roman','slp1')
				rep = transcoder.transcoder_processString(rep,'slp1','deva')
				html = html.replace('<body><b>'+ital+'</b>','<body><b>'+rep+'</b>BREAK')
				html = re.sub(u'<body><b>([^<]*)।</b>',u'<body><b>\g<1></b>',html) # vei
		if dictId in ['acc','ap90','ben','bhs','bur','cae','ccs','gra','gst','ieg','inm','mci','mw72','pd','pe','pgn','pui','pwg','vei']:
			html = transcoder.transcoder_processString(html,'as','roman')
			html = html.replace(u'ç',u'ś')
			html = html.replace(u'Ç',u'Ś')
			html = html.replace(u'¦',u'') # ccs
			html = html.replace(u'[Pagē-',u'[Page 1-')
			html = html.replace(u'[Pagė',u'[Page 1-')
			html = html.replace(u'C¤:',u'Comm.')
			html = html.replace(u'n1',u'ṅ')
			html = html.replace(u'm5',u'ṃ') # ben
			if not dictId in ['pui']:
				html = html.replace(' --','BREAK --') # ap90
			html = html.replace(' <b>1</b>','BREAK<b>1</b>')
			html = re.sub('(<i>--[^<]*</i>)','BREAK\g<1>',html)
			html = html.replace('] ',']BREAK')
			html = html.replace('<s>(</s>','(')
			html = html.replace('<s>) </s>',') ')
			html = html.replace(u'ṛi',u'ṛ')
			
		if dictId in ['bur']:
			html = html.replace(u'|',u'')
		if dictId in ['stc']:
			html = transcoder.transcoder_processString(html,'as','roman')
			html = html.replace('|','')
		if dictId in ['cae']:
			html = html.replace(u'·',u'')
		if dictId in ['gst']:
			html = html.replace(' ^','BREAK ^')
		if dictId in ['mwe']:
			html = re.sub(u'[)]([^ ,.;\n])',u') \g<1>',html)
		html = html.replace('- ','')
		html = re.sub('[ ]+',' ',html)
		html = html.replace('&amp;','&')
		html = html.replace(u'î',u'ī')
		html = html.replace(u'â',u'ā')
		html = re.sub('[<][^>]*[>]','',html)
		if dictId in ['ap']:
			html = html.replace('- -','-')
		if dictId in ['pd']:
			html = re.sub('^[.]','',html)
		if dictId in ['ae']:
			html = html.replace('- -','') # अंगीकार- -द्योतक
		if dictId in ['mwe']:
			html = html.replace(u'. — ', u'. BREAK — ')
		html = html.replace('BREAK','<BR>')
		if dictId in ['gra']:
			html = transcoder.transcoder_processString(key2,'slp1','deva')+'<BR>'+html
		html = html.replace('<BR><BR>','<BR>')
		if production == '0':
			html = html.replace('<BR>','\n')
		outputfile.write(heading+'\n')
		outputfile.write(html+'\n\n')
	outputfile.close()
