##from gevent import monkey; monkey.patch_all()
#import ptvsd
#
## 5678 is the default attach port in the VS Code debug configurations
#print("Waiting for debugger attach")
#ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)
#ptvsd.wait_for_attach()
#breakpoint()




def main():
	import creAI.globals
	creAI.globals.cli_mode = False
	import eel
	import creAI.ui
	eel.init('web')
	eel.start('index.html', block=False)
	import creAI.plugins
	while True:
		eel.sleep(10)

if __name__ == '__main__':
	main()

