import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import com.sun.net.httpserver.HttpExchange;

// remove um cliente
public class Deleter extends Handler {

	@Override
	public void handlePost(HttpExchange e) throws IOException
	{
		int length = Integer.parseInt(e.getRequestHeaders().get("Content-Length").get(0));
		byte[] in = new byte[length];

		InputStream i = e.getRequestBody();
		i.read(in);
		String token = new String(in);

		if (!Client.remove(token))
			e.sendResponseHeaders(404, 0); // Not Found
		else
			e.sendResponseHeaders(200, 0); // OK

		e.getResponseBody().close();
	}

}
