##from gevent import monkey; monkey.patch_all()
#import ptvsd
#
## 5678 is the default attach port in the VS Code debug configurations
#print("Waiting for debugger attach")
#ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)
#ptvsd.wait_for_attach()
#breakpoint()


import creAI.app

if __name__ == '__main__':
	creAI.app.run()

