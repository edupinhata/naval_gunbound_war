import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import com.sun.net.httpserver.HttpExchange;

// remove um cliente
public class Deleter extends Handler {

	@Override
	public void handlePost(HttpExchange e) throws IOException
	{
		if (!Client.remove(getBody(e)))
			e.sendResponseHeaders(404, 0); // Not Found
		else
			e.sendResponseHeaders(200, 0); // OK

		e.getResponseBody().close();
	}

}
