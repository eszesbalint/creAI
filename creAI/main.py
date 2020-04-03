if __name__ == '__main__':
	import eel
	eel.init('ui')
	eel.start('index.html', block=False)

	import creAI.Plugins

	while True:
		eel.sleep(10)

