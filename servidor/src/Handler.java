import java.io.IOException;
import java.util.Map;
import java.util.LinkedHashMap;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;

public abstract class Handler implements HttpHandler {

	// obtém os argumentos do link solicitado, (ex. token na classe Streamer)
	protected static Map<String, String[]> getParams(HttpExchange e)
	{
		Map<String, String[]> params =
			new LinkedHashMap<String, String[]>();

		// argumentos são separados por &
		String[] pairs = e.getRequestURI().getQuery().split("&");
		for (String s : pairs) {
			// argumento e respectivo valor são separados por =
			String[] pair = s.split("=");
			// múltiplos valores são separados por ,
			params.put(pair[0], pair[1].split(","));
		}

		return params;
	}

	// redireciona a requisição pro método adequado, dependendo do método HTTP
	// utilizado (GET ou POST). subclasses devem re-implementar handleGet ou
	// handlePost, caso contrário um erro será retornado.
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

	// envia um erro de método HTTP não permitido/implementado.
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
