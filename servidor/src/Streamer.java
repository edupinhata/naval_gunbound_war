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

		// obtém os argumentos da requisição
		Map<String, String[]> p = getParams(e);

		// necessita do argumento token
		String[] t = p.get("token");
		if (t == null) {
			e.sendResponseHeaders(404, 0);
			o.close();
			return;
		}

		// envia ok, mas não fecha a conexão
		e.sendResponseHeaders(200, 0);

		// adiciona conexão a um cliente se o token correspondente existir
		Client.addStream(Integer.parseInt(t[0]), o);

		//TODO verificar se o token existe, se não existir, fechar a conexão
	}

}
