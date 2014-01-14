import java.io.IOException;
import java.io.InputStream;
import com.sun.net.httpserver.HttpExchange;

public class Broadcaster extends Handler {

	@Override
	protected void handlePost(HttpExchange e) throws IOException
	{
		Client.broadcast(getBody(e));

		// TODO broadcast retornar booleano
		e.sendResponseHeaders(200, 0); // OK
		e.getResponseBody().close();
	}

}
