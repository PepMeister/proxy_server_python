import socket, sys
import threading

try:
	listening_port = int(input("[->] Enter listening port number:"))
except KeyboardInterrupt:
	print("\n[!] User requested an interrupt.")
	sys.exit(0)

max_conn = 5
buf_size = 8192


def start():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print("[i] Socket init..")
		s.bind(('', listening_port))
		print("[i] Sockets binded..")
		s.listen(max_conn)
		print("[i] Server started at:", listening_port)
	except Exception:
		print("[!] Unable initialize socket.")
		sys.exit(2)

	while(True):
		try:
			print("..")
			conn, addr = s.accept()
			data = conn.recv(buf_size)
			T = threading.Thread(target=conn_details, args=(conn, data, addr))
			T.start()
		except KeyboardInterrupt:
			s.close()
			print("[!]Server shutting down.")
			sys.exit(1)
	s.close()


def conn_details(conn, data, addr):
	try:
		first_line = str(data).split('\n')[0]
		url = first_line.split(' ')[1]
		http_pos = url.find("://")
		if (http_pos==-1):
			temp=url
		else:
			temp=url[(http_pos+3):]

		port_pos = temp.find(":")
		webserver_pos = temp.find("/")

		if (webserver_pos==-1):
			webserver_pos=len(temp)

		webserver = ""
		port = -1

		if(port_pos==-1 or webserver_pos < port_pos):
			port = 80
			webserver = temp[:webserver_pos]
		else:
			port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
			webserver = temp[:port_pos]

		proxy_server(webserver, port, conn, addr, data)
	except KeyboardInterrupt:
		print("[!] Exit.")


def proxy_server(webserver, port, conn, addr, data):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((webserver, port))
		s.send(data)

		while(True):
			reply = s.recv(buf_size)

			if(len(reply) >0):

				conn.send(reply)

				dar = float(len(reply))
				dar = float(dar / 1024)
				dar = "%.3s"%(str(dar))
				dar = "%s KB" % dar

				print("[i] Request done: ",str(addr[0])," => ",str(dar)," =>", webserver)
			else:
				break

		s.close()
		conn.close()

	except socket.error:
		s.close()
		conn.close()
		sys.exit(1)


if __name__=='__main__':
	start()