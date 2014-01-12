import java.io.IOException;
import java.io.OutputStream;
import com.sun.net.httpserver.HttpExchange;

public class Tokenizer extends Handler {

	protected static Integer getToken(HttpExchange e)
	{
		return e.getRemoteAddress().toString().hashCode();
	}

	@Override
	public void handlePost(HttpExchange e) throws IOException
	{
		OutputStream o = e.getResponseBody();

		Integer t = getToken(e);
		new Client(t);

		byte[] b = t.toString().getBytes();
		e.sendResponseHeaders(200, b.length);
		o.write(b);

		o.close();
	}

}
