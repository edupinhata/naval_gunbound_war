import java.io.IOException;
import java.util.Map;
import java.util.LinkedHashMap;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;

public abstract class Handler implements HttpHandler {

	protected static Map<String, String[]> getParams(HttpExchange e)
	{
		Map<String, String[]> params =
			new LinkedHashMap<String, String[]>();

		String[] pairs = e.getRequestURI().getQuery().split("&");
		for (String s : pairs) {
			String[] pair = s.split("=");
			params.put(pair[0], pair[1].split(","));
		}

		return params;
	}

	@Override
	public void handle(HttpExchange e) throws IOException
	{
		String method = e.getRequestMethod();
		if (method.equalsIgnoreCase("GET")) {
			handleGet(e);
		} else if (method.equalsIgnoreCase("POST")) {
			handlePost(e);
		} else {
			sendUnavaliable(e);
		}
	}

	private void sendUnavaliable(HttpExchange e) throws IOException
	{
		e.sendResponseHeaders(405, 0);
		e.getResponseBody().close();
	}

	protected void handleGet(HttpExchange e) throws IOException
	{
		sendUnavaliable(e);
	}

	protected void handlePost(HttpExchange e) throws IOException
	{
		sendUnavaliable(e);
	}

}
