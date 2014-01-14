import java.util.Map;
import java.util.Arrays;
import java.io.IOException;
import java.io.OutputStream;
import com.sun.net.httpserver.HttpExchange;

public class Streamer extends Handler {

	@Override
	public void handleGet(HttpExchange e) throws IOException
	{
		OutputStream o = e.getResponseBody();

		// necessita do argumento token. se não houver, manda erro e fecha o
		// stream.
		Map<String, String[]> p = getParams(e);
		String[] t = p.get("token");
		if (t == null) {
			e.sendResponseHeaders(400, 0); // Bad Request
			o.close();
			return;
		}

		// procura cliente correspondente ao token. se não achar, manda erro e
		// fecha o stream.
		if (!Client.addStream(t[0], o)) {
			e.sendResponseHeaders(404, 0); // Not Found
			o.close();
			return;
		}

		// manda ok e deixa o stream aberto pro cliente receber mensagens.
		e.sendResponseHeaders(200, 0); // OK
	}

}
