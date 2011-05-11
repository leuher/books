# -*- coding: utf-8 -*-

from __future__ import print_function
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import sys
import os

import config
import index
import search
import epub

class RpcSearcher(object):
	def __init__(self, index_path):
		self.idx = index.Index(index_path)
		
	def __makeResultEntry(self, docid):
		entry = {'id':docid}
		file_path = self.idx.document(docid)
		info = epub.get_info(file_path)
		entry['author'] = info.authors()
		entry['title'] = info.titles()
		return entry
	
	def search(self, keywords, page=0, resultsOnPage=10):
		docs = search.search(keywords, self.idx)
		docs = docs[page*resultsOnPage:(page+1)*resultsOnPage]
		result = [self.__makeResultEntry(docid) for docid in docs]
		return result
		
	def getFilePath(self, docid):
		return self.idx.document(docid)

class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/RPC2',)
	
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print ('Usage: python', sys.argv[0], 'path/to/lib')
		os._exit(os.EX_USAGE)
	
	server = SimpleXMLRPCServer((config.RPCServerHost, config.RPCServerPort), requestHandler=RequestHandler)
	print('listening on port %d...' % config.RPCServerPort)
	server.register_introspection_functions()
	
	server.register_instance(RpcSearcher(sys.argv[1].decode(config.SystemCodePage)))
	
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print('stopping server...')