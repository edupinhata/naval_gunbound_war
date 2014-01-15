import java.net.*;
import java.util.concurrent.*;
import com.sun.net.httpserver.*;

public class Server {
	
	public static void main(String[] args) throws Exception
	{
		// cria servidor na porta 8000 (HTTP)
		HttpServer s = HttpServer.create(new InetSocketAddress(8000), 0);

		// permite multi-threading, caso contrário o servidor bloqueia a cada
		// requisição
		s.setExecutor(Executors.newCachedThreadPool());

		// cria contextos e respectivos handlers
		s.createContext("/token", new Tokenizer());
		s.createContext("/delete", new Deleter());
		s.createContext("/stream", new Streamer());
		s.createContext("/broadcast", new Broadcaster());

		// roda o servidor
		s.start();
	}

}
