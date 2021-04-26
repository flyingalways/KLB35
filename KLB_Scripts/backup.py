import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os
import shutil
import zipfile
PY3 = sys.version_info[0] >= 3
if ( PY3 ):
	from io import StringIO
else:
	from StringIO import StringIO
import gzip
import requests
import io
import tempfile
import threading

import pyxbmct
import sys
import json

global MyAddon,zipdir,zipfichero,guarda,shownotify,threadnotify,CancelledError,BufferReader,progress,sube
global iconpath,pathfondos
global zipf


addon_id = 'script.kelebek'

if PY3:
	import zipfile
else:
	#xbmc.log('[%s] %s' % ('PYTHON 2', ''), 2)
	from lib import zipfile

iconpath = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
pathfondos = xbmc.translatePath(os.path.join('special://home/addons',addon_id,'resources'))

wdp = xbmcgui.DialogProgress()
nitems = 0
nitem = 0

class MyAddon(pyxbmct.AddonDialogWindow):

	def __init__(self, title=''):
		super(MyAddon, self).__init__(title)
		self.setGeometry(750, 300, 4, 3)
		self.set_controls()
		self.set_navigation()
		# Connect a key action (Backspace) to close the window.
		self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

	def set_controls(self):
	
		self.fondo=pyxbmct.Image(os.path.join(pathfondos,'fondoceleste.png'))
		self.placeControl(self.fondo,0,0,4,3)
	
		# Demo for PyXBMCt UI controls.
		no_int_label = pyxbmct.Label('BACKUP KODI', alignment=pyxbmct.ALIGN_CENTER,
											textColor='0xFFFBFCFA')
		self.placeControl(no_int_label, 0, 0, 1, 3)
		#
		# Button
		self.bguarda = pyxbmct.Button('Guardar Archivo',
											textColor='0xFFFBFCFA', 
											focusedColor='0xFF238303',
											noFocusTexture=os.path.join(pathfondos,'bgris.png'),
											focusTexture=os.path.join(pathfondos,'bnaranja.png'))
		self.placeControl(self.bguarda, 1, 0,1,1)
		# Connect control to close the window.
		self.connect(self.bguarda, self.guarda)
		#
		self.bsube = pyxbmct.Button('Subir Archivo',
											textColor='0xFFFBFCFA', 
											focusedColor='0xFF238303',
											noFocusTexture=os.path.join(pathfondos,'bgris.png'),
											focusTexture=os.path.join(pathfondos,'bnaranja.png'))
		self.placeControl(self.bsube, 1, 2,1,1)
		# Connect control to close the window.
		self.connect(self.bsube, self.sube)
		
		self.url = pyxbmct.Label('',textColor='0xFFFF0000')
		self.placeControl(self.url, 2, 0, 1, 3)
		self.url.setVisible(False)
		
		self.bsalir = pyxbmct.Button('Salir',
											textColor='0xFFFBFCFA', 
											focusedColor='0xFF238303',
											noFocusTexture=os.path.join(pathfondos,'bgris.png'),
											focusTexture=os.path.join(pathfondos,'bnaranja.png'))
		self.placeControl(self.bsalir, 3, 1,1,1)
		# Connect control to close the window.
		self.connect(self.bsalir, self.close)

	def set_navigation(self):
		# Set navigation between controls
		#self.button.controlUp(self.slider)
		#self.button.controlDown(self.radiobutton)
		#self.radiobutton.controlUp(self.button)
		#self.radiobutton.controlDown(self.slider)
		#self.slider.controlUp(self.radiobutton)
		#self.slider.controlDown(self.button)
		self.bguarda.setNavigation(self.bsalir,self.bsalir,self.bsube,self.bsube)
		self.bsube.setNavigation(self.bsalir,self.bsalir,self.bguarda,self.bguarda)
		self.bsalir.setNavigation(self.bguarda,self.bguarda,self.bguarda,self.bguarda)
		#self.autoNavigation()
		# Set initial focus
		self.setFocus(self.bguarda)

	def setAnimation(self, control):
		# Set fade animation for all add-on window controls
		control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=500',),
								('WindowClose', 'effect=fade start=100 end=0 time=500',)])
	def guarda(self):
		guarda(0)
		
	def sube(self):
		sube(self)


def shownotify(message,seconds):
	xbmc.executebuiltin('XBMC.Notification(%s, %s, %s, %s)' % ('KELEBEK' , message, str(seconds), iconpath))

def threadnotify(message,seconds):
	dnotifythread = threading.Thread(target=shownotify,args=(message,seconds))
	dnotifythread.start()  # ...Start the thread, invoke the run method

def zipdir(path, exento=''):
	global wdp
	global nitem
	global nitems
	global zipf
	try:
		# ziph is zipfile handle
		for root, dirs, files in os.walk(path):
			#xbmc.log('[%s] %s %s %s' % ('ROOT:', root, dirs, files), 2)
			for file in files:
				if ( wdp.iscanceled() ): 
					return
				nitem = nitem + 1
				progress = nitem / float(nitems) * 100
				# Esto es para probar si poniendo esta linea de abajo no se duplica el mensaje
				#wdp.update(int(progress))
				wdp.update(int(progress),'Copiando [COLOR yellow]%s[/COLOR]'%file + ' Por favor, espere...')
				if ( os.path.exists(os.path.join(root, file)) ):
					if ( exento not in file ):
						try:
							if ( os.path.exists(os.path.join(root, file)) ):
								xbmc.log('BCK 7 E:'+os.path.join(root, file),2)
							else:
								xbmc.log('BCK 7 NE:'+os.path.join(root, file),2)
							#xbmc.log('[%s] %s' % ('FILE:', file), 2)
							zipf.write(os.path.join(root, file))
						except Exception:
							_, e, _ = sys.exc_info()
							xbmc.log('[%s] %s' % ('EXCEPTION:', str(e)), 2)
				else:
					xbmc.log('[%s] %s %s %s' % ('FILE NOT EXISTS:', root, dirs, file), 2)
	except Exception:
		_, e, _ = sys.exc_info()
		xbmc.log('[%s] %s' % ('EXCEPTION:', str(e)), 2)
		#xbmc.executebuiltin('Notification(%s, %s)'%('ERROR:',str(e)))
		#raise Exception(str(e))


def guarda(flag):
	global wdp
	global nitem
	global nitems
	global addon_id
	global zipf
	dialog = xbmcgui.Dialog()
	if ( flag==0 ):
		ndir = dialog.browse(3, 'KELEBEK', '')
	else:
		ndir=xbmc.translatePath('special://home/addons/' + addon_id)
		fileup=xbmc.translatePath(os.path.join('special://home/addons/' + addon_id,'Backup_KLB.zip'))
	#xbmc.log('[%s] %s' % ('DIR:', ndir), 2)
	try:
		if ( ndir != '' ):
			#xbmc.log('[%s] %s' % ('ZIP:', os.path.join(ndir,'Backup')), 2)
			#shutil.make_archive(os.path.join(ndir,'Backup.zip'), 'zip', xbmc.translatePath('special://home/addons/'))
			if ( os.path.exists(os.path.join(ndir,'Backup_KLB.zip')) ):
				os.remove(os.path.join(ndir,'Backup_KLB.zip'))
			xbmc.log('BCK 1:'+os.path.join(ndir,'Backup_KLB.zip'),2)
			zipf = zipfile.ZipFile(os.path.join(ndir,'Backup_KLB.zip'), 'w', zipfile.ZIP_DEFLATED)
			xbmc.log('BCK 2',2)
			os.chdir(xbmc.translatePath('special://home'))
			wdp.create("BACKUP KELEBEK",'Contando Numero de Archivos. Por favor, espere...')
			wdp.update(0)
			nitems = 0
			nitem = 0
			for base, dirs, files in os.walk('./addons/'):
				for file in files:
					nitems = nitems + 1
					wdp.update(0,'Numero de Archivos: '+str(nitems))
			for base, dirs, files in os.walk('./userdata/'):
				for file in files:
					nitems = nitems + 1
					wdp.update(0,'Numero de Archivos: '+str(nitems))
			xbmc.log('BCK 3',2)
			zipdir('./addons/', 'Backup_KLB')
			xbmc.log('BCK 4',2)
			if ( not wdp.iscanceled() ):
				xbmc.log('BCK 5',2)
				zipdir('./userdata/', 'Backup_KLB')
				xbmc.log('BCK 6',2)
			zipf.close()
			wdp.close()
			if ( not wdp.iscanceled() ):
				if ( flag==0 ):
					threadnotify('BACKUP FINISHED',4000)
					dialog.ok('BACKUP FINISHED', '[COLOR yellow]Copia realizada:[/COLOR] [COLOR blue]' + str(nitems) + '[/COLOR] [COLOR yellow]Archivos copiados.[/COLOR]')
				return True
			else:
				if ( os.path.isfile(os.path.join(ndir,'Backup_KLB.zip')) ):
					os.remove(os.path.join(ndir,'Backup_KLB.zip'))
				dialog.ok('BACKUP CANCELADO', '[COLOR yellow]Backup cancelado[/COLOR]')
				return False
	except Exception:
		_, e, _ = sys.exc_info()
		zipf.close()
		wdp.close()
		if ( os.path.isfile(os.path.join(ndir,'Backup_KLB.zip')) ):
			os.remove(os.path.join(ndir,'Backup_KLB.zip'))
		xbmc.log('[%s] %s' % ('EXCEPTION:', str(e)), 2)
		xbmc.executebuiltin('Notification(%s, %s)'%('ERROR:',str(e)))
		return False
		
	
	
'''
# an adapter which makes the multipart-generator issued by poster accessable to requests
# based upon code from http://stackoverflow.com/a/13911048/1659732
class IterableToFileAdapter(object):
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.length = iterable.total
 
    def read(self, size=-1):
        return next(self.iterator, b'')
 
    def __len__(self):
        return self.length
 
# define a helper function simulating the interface of posters multipart_encode()-function
# but wrapping its generator with the file-like adapter
def multipart_encode_for_requests(params, boundary=None, cb=None):
    datagen, headers = multipart_encode(params, boundary, cb)
    return IterableToFileAdapter(datagen), headers
 
 
 
# this is your progress callback
def progress(param, current, total):
    if not param:
        return
    # check out http://tcd.netinf.eu/doc/classnilib_1_1encode_1_1MultipartParam.html
    # for a complete list of the properties param provides to you
    #print "{0} ({1}) - {2:d}/{3:d} - {4:.2f}%".format(param.name, param.filename, current, total, float(current)/float(total)*100)
	global wdp
	#print("{0} / {1}".format(size, progress))
	if ( wdp.iscanceled() ): 
		raise CancelledError('The upload was cancelled.')
	progress = float(current)/float(total)*100  
	wdp.update(int(progress),"Subiendo Backup ",'[COLOR red]Backup_KLB.zip[/COLOR]', 'Por favor, espera...')
'''

'''
class upload_in_chunks(object):
    def __init__(self, filename, chunksize=1 << 13):
        self.filename = filename
        self.chunksize = chunksize
        self.totalsize = os.path.getsize(filename)
        self.readsofar = 0

    def __iter__(self):
        with open(self.filename, 'rb') as file:
            while True:
                data = file.read(self.chunksize)
                if not data:
                    sys.stderr.write("\n")
                    break
                self.readsofar += len(data)
                percent = self.readsofar * 1e2 / self.totalsize
                xbmc.log("\r{percent:3.0f}%".format(percent=percent))
                yield data

    def __len__(self):
        return self.totalsize
		
class IterableToFileAdapter(object):
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.length = len(iterable)

    def read(self, size=-1): # TBD: add buffer for `len(data) > size` case
        return next(self.iterator, b'')

    def __len__(self):
        return self.length
'''


class CancelledError(Exception):
	def __init__(self, msg):
		self.msg = msg
		Exception.__init__(self, msg)

	def __str__(self):
		return self.msg

	__repr__ = __str__

class BufferReader(io.BytesIO):
	global wdp
	def __init__(self, buf=b'',
				 callback=None,
				 cb_args=(),
				 cb_kwargs={}):
		self._callback = callback
		self._cb_args = cb_args
		self._cb_kwargs = cb_kwargs
		self._progress = 0
		self._len = len(buf)
		io.BytesIO.__init__(self, buf)

	def __len__(self):
		return self._len

	def read(self, n=-1):
		if ( wdp.iscanceled() ): 
			raise CancelledError('The upload was cancelled.')
		chunk = io.BytesIO.read(self, n)
		self._progress += int(len(chunk))
		self._cb_kwargs.update({
			'size'    : self._len,
			'progress': self._progress
		})
		if self._callback:
			try:
				self._callback(*self._cb_args, **self._cb_kwargs)
			except: # catches exception from the callback
				raise CancelledError('The upload was cancelled.')
		return chunk


def progress(size=None, progress=None):
	global wdp
	#print("{0} / {1}".format(size, progress))
	if ( wdp.iscanceled() ): 
		raise CancelledError('The upload was cancelled.')
	progress = progress / float(size) * 100  
	wdp.update(int(progress),'Subiendo Backup ' + '\n' +'[COLOR red]Backup_KLB.zip[/COLOR]'+ '\n' +'Por favor, espera...')



def sube(ventana):
	global addon_id
	try:
		global wdp
		fileup=xbmc.translatePath(os.path.join('special://home/addons/' + addon_id,'Backup_KLB.zip'))
		if ( guarda(1) ):
			ventana.url.setLabel('SUBIENDO ARCHIVO. POR FAVOR, ESPERE...')
			ventana.url.setVisible(True)
			wdp.create("BACKUP KELEBEK",'Subiendo Backup. Por favor, espere...')
			wdp.update(0)
			url = 'https://api.anonfiles.com/upload'
			pfileup=open(fileup, 'rb')
			files = {'file': (pfileup)}
			#xbmc.log("[UPLOADING]"+ fileup,2)
			#r = requests.post(url, files=files)
			
			
			files = {"file": ("Backup_KLB.zip", pfileup.read())}
			(data, ctype) = requests.packages.urllib3.filepost.encode_multipart_formdata(files)
			headers = {	"Content-Type": ctype}
			body = BufferReader(data, progress)
			r = requests.post(url, data=body, headers=headers)
			'''
			headers = {	"bin": 'custombin', "filename": 'BCKKLB.zip'}
			url='https://filebin.net/'
			#r = requests.post(url, data=body, headers=headers)
			r = requests.post(url, data=pfileup, headers=headers)
			'''
			
			'''
			# load posters encode-function
			from poster.encode import multipart_encode
			# generate headers and gata-generator an a requests-compatible format
			# and provide our progress-callback
			datagen, headers = multipart_encode_for_requests({
				"myfileupl":pfileup,
			}, cb=progress)
			 
			# use the requests-lib to issue a post-request with out data attached
			#r = requests.post(
			#	'https://httpbin.org/post',
			#	auth=('user', 'password'),
			#	data=datagen,
			#	headers=headers
			#)
			r = requests.post(
				url,
				data=datagen,
				headers=headers
			)
			'''
			'''
			xbmc.log('PPV1',2)
			it = upload_in_chunks(__file__, 10)
			xbmc.log('PPV2',2)
			r = requests.post(url, data=IterableToFileAdapter(it))
			xbmc.log('PPV3',2)
			#r = requests.post(url,data=upload_in_chunks(fileup, chunksize=10))
			'''
			#xbmc.log('TEXT',2)
			#xbmc.log(repr(r.text),2)
			if ( not wdp.iscanceled() ):
				resp = json.loads(r.text)
				if resp['status']:
					wdp.close()
					urlshort = resp['data']['file']['url']['short']
					urllong = resp['data']['file']['url']['full']
					#xbmc.log('[SUCCESS] Short URL: '+urlshort,2)
					ventana.url.setLabel('SUBIDO A '+urlshort)
					ventana.url.setVisible(True)
				else:
					message = resp['error']['message']
					errtype = resp['error']['type']
					xbmc.log('[ERROR] '+message+' '+errtype,2)
					wdp.close()
					ventana.url.setLabel('ERROR: '+message+' '+errtype)
					ventana.url.setVisible(True)
			else:
				ventana.url.setLabel('SUBIDA CANCELADA')
				ventana.url.setVisible(True)
			pfileup.close()
			os.remove(fileup)
		else:
			#pfileup.close()
			os.remove(fileup)
			xbmc.executebuiltin('Notification(%s, %s)'%('ERROR:','Se ha producido un error'))
	except Exception:
		_, e, _ = sys.exc_info()
		xbmc.log('[%s] %s' % ('EXCEPTION:', str(e)), 2)
		xbmc.executebuiltin('Notification(%s, %s)'%('ERROR:',str(e)))
		#pfileup.close()
		#os.remove(fileup)
		if ( wdp.iscanceled ):
			ventana.url.setLabel('ERROR/SUBIDA CANCELADA: '+str(e))
			ventana.url.setVisible(True)
		#wdp.close()


try:
	window = MyAddon('')
	window.doModal()
	# Destroy the instance explicitly because
	# underlying xbmcgui classes are not garbage-collected on exit.
	del window
except Exception:
	_, e, _ = sys.exc_info()
	xbmc.log('[%s] %s' % ('EXCEPTION:', str(e)), 2)
	xbmc.executebuiltin('Notification(%s, %s)'%('ERROR:',str(e)))

