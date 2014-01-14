import java.io.IOException;
import java.util.Map;
import java.util.LinkedHashMap;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;

public abstract class Handler implements HttpHandler {

	// retorna o tamanho do corpo da mensagem
	protected static int getLength(HttpExchange e)
	{
		try {
			return Integer.parseInt(e.getRequestHeaders().get("Content-Length").get(0));
		} catch (Exception ex) {
			ex.printStackTrace();
			return 0;
		}
	}

	// lê e retorna o corpo da mensagem
	protected static String getBody(HttpExchange e)
	{
		try {
			int length = getLength(e);
			byte[] in = new byte[length];
			e.getRequestBody().read(in, 0, length);
			return new String(in);
		} catch (Exception ex) {
			ex.printStackTrace();
			return new String();
		}
	}

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
