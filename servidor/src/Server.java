import java.net.InetSocketAddress;
import java.util.concurrent.Executors;
import com.sun.net.httpserver.HttpServer;

public class Server {
	
	public static void main(String[] args) throws Exception
	{
		HttpServer s = HttpServer.create(new InetSocketAddress(80), 0);
		s.setExecutor(Executors.newCachedThreadPool());

		s.createContext("/token", new Tokenizer());
		s.createContext("/stream", new Streamer());
		s.createContext("/broadcast", new Broadcaster());

		s.start();
	}

}
