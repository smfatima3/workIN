"""Tests the real HTTP/JSON path with a labeled local stub; no model validation claim."""
from http.server import BaseHTTPRequestHandler,HTTPServer
import threading,json
from mrs.policy import Policy
from mrs.common import Log

def test_http_path_usage_and_stateless_messages(tmp_path,monkeypatch):
 seen=[]
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_POST(self):
   body=json.loads(self.rfile.read(int(self.headers['Content-Length'])));seen.append(body)
   response={'model':'contract-test-stub','choices':[{'message':{'content':json.dumps({'belief':'unknown','store':False,'share':False,'reason':'HTTP contract stub'})}}],
             'usage':{'prompt_tokens':11,'completion_tokens':7}}
   self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(response).encode())
 server=HTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  monkeypatch.setenv('MRS_API_BASE',f'http://127.0.0.1:{server.server_port}/v1')
  policy=Policy({'provider':'openai_compatible','model':'contract-test-stub','chat_template_kwargs':{'enable_thinking':False},'top_p':.8,'top_k':20},Log(tmp_path/'events.jsonl'))
  for i in range(2):policy.ask('learn',{'records':[]},i)
  assert policy.tokens_in==22 and policy.tokens_out==14
  assert all(len(x['messages'])==2 for x in seen)
  assert all(x['chat_template_kwargs']=={'enable_thinking':False} and x['top_p']==.8 and x['top_k']==20 for x in seen)
  assert not policy.usage_missing
 finally:server.shutdown();thread.join();server.server_close()
