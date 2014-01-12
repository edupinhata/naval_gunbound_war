import java.net.InetSocketAddress;
import java.util.concurrent.Executors;
import com.sun.net.httpserver.HttpServer;

public class Server {
	
	public static void main(String[] args) throws Exception
	{
		// cria servidor na porta 80 (HTTP)
		HttpServer s = HttpServer.create(new InetSocketAddress(80), 0);

		// permite multi-threading, caso contrário o servidor bloqueia a cada
		// requisição
		s.setExecutor(Executors.newCachedThreadPool());

		// cria contextos e respectivos handlers
		s.createContext("/token", new Tokenizer());
		s.createContext("/stream", new Streamer());
		s.createContext("/broadcast", new Broadcaster());

		// roda o servidor
		s.start();
	}

}
