import java.io.IOException;
import java.io.InputStream;
import com.sun.net.httpserver.HttpExchange;

public class Broadcaster extends Handler {

	@Override
	protected void handlePost(HttpExchange e) throws IOException
	{
		String h = e.getRequestHeaders().get("Content-Length").get(0);
		int length = Integer.parseInt(h);

		byte[] data = new byte[length];
		e.getRequestBody().read(data);

		Client.broadcast(new String(data));

		e.sendResponseHeaders(200, 0);
		e.getResponseBody().close();
	}

}
