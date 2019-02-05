from __future__ import print_function
import sys
import zerorpc
import model as CREAI


model = CREAI.CreAIModel()

class CreAIAPI(object):
    def generate(self, attributes):
        return str(model.generate())

def main():
    port = 4242
    server_address = 'tcp://127.0.0.1:' + '{}'.format(port)
    server = zerorpc.Server(CreAIAPI())
    server.bind(server_address)
    print('Server running on {}'.format(server_address))
    server.run()

if __name__ == '__main__':
    main()
