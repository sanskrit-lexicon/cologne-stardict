# This Python file uses the following encoding: utf-8
"""
Usage:
python add_endline.py
e.g.
python add_endline.py
"""

if __name__=="__main__":
	dictList = ['acc','ae','ap','ap90','ben','bhs','bop','bor','bur','cae','ccs','gra','gst','ieg','inm','krm','mci','md','mw','mw72','mwe','pd','pe','pgn','pui','pw','pwg','sch','shs','skd','snp','stc','vcp','vei','wil','yat']
	for dic in dictList:
		fin = open('production/'+dic+'.babylon','r',encoding='utf-8')
		data = fin.readlines()
		fin.close()
		if len(data) % 3 == 0:
			fout = open('production/'+dic+'.babylon','w',encoding='utf-8')
			dat = ''.join(data)
			dat = dat+'\n'
			print(dic)
			fout.write(dat)
			fout.close()

