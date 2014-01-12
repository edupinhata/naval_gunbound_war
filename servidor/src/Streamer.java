import java.util.Map;
import java.util.Arrays;
import java.io.IOException;
import java.io.OutputStream;
import com.sun.net.httpserver.HttpExchange;

public class Streamer extends Handler {

	@Override
	public void handleGet(HttpExchange e) throws IOException
	{
		Map<String, String[]> p = getParams(e);
		OutputStream o = e.getResponseBody();

		String[] t = p.get("token");
		if (t == null) {
			e.sendResponseHeaders(404, 0);
			o.close();
			return;
		}

		e.sendResponseHeaders(200, 0);
		Client.addStream(Integer.parseInt(t[0]), o);
	}

}
