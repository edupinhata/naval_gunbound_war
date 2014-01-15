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
		Game g = new Game();
		s.createContext("/token", new Tokenizer(g));
		s.createContext("/delete", new Deleter(g));
		s.createContext("/stream", new Streamer(g));
		s.createContext("/broadcast", new Broadcaster(g));

		// roda o servidor
		s.start();
	}

}
